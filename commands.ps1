az group create --name rg-web-app-avaya-bot --location eastus

az acr create --resource-group rg-web-app-avaya-bot --name webappavaya --sku Basic --admin-enabled true

$ACR_PASSWORD=$(az acr credential show --resource-group rg-web-app-avaya-bot --name webappavaya --query "passwords[?name == 'password'].value" --output tsv)

az acr build --resource-group rg-web-app-avaya-bot --registry webappavaya  --image avayabot:v1 .

az appservice plan create --name webappavayaplan --resource-group rg-web-app-avaya-bot --sku B1 --is-linux

az webapp create --resource-group rg-web-app-avaya-bot --plan webappavayaplan --name avayabotv1 --docker-registry-server-password $ACR_PASSWORD --docker-registry-server-user webappavaya --role acrpull --deployment-container-image-name webappavaya.azurecr.io/avayabot:v1

docker build -t avayabot:v3 .