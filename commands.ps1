$RG_NAME="RG-OpenAI-DEV"
$LOCATION="eastus"
$ACR_NAME="acrdevrgopenaidev"
$WEB_APP_NAME="WebappOpenAITeamsBot"
$PLAN_NAME="AppServicePlanOpenAITeamsBot"
$BOT_NAME="OpenAITeamsBot"




az group create --name rg-web-app-avaya-bot --location eastus ## not needed if you already have a resource group ##

az acr create --resource-group $RG_NAME --name $ACR_NAME --sku Basic --admin-enabled true ##

$ACR_PASSWORD=$(az acr credential show --resource-group $RG_NAME --name $ACR_NAME --query "passwords[?name == 'password'].value" --output tsv)

az acr build --resource-group $RG_NAME --registry $ACR_NAME  --image avayabot:v3 . ##

az appservice plan create --name $PLAN_NAME --resource-group $RG_NAME --sku B1 --is-linux ##

az webapp create --resource-group $RG_NAME --plan $PLAN_NAME --name $WEB_APP_NAME --docker-registry-server-password $ACR_PASSWORD --docker-registry-server-user $ACR_NAME --role acrpull --deployment-container-image-name webappavaya.azurecr.io/avayabot:v3

az webapp config appsettings set --name thecodebuzz-ui --resource-group thecodebuzz --settings "MICROSOFT_APP_ID=<<APP_ID>>" "MICROSOFT_APP_PASSWORD=<<APP_PASSWORD>>"

docker build -t avayabot:v3 .

docker run -it --publish 3978:3978 avayabot:v3
docker run -it --publish 3978:3978 --env-file .evn avayabot:v3

ngrok http 3978 --host-header="localhost:3978"


az provider register --namespace Microsoft.BotService 