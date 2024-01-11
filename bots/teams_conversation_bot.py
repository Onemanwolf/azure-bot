# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from http import HTTPStatus
import requests
from aiohttp import web
from aiohttp.web import Request, Response, json_response
import json
from typing import List
from botbuilder.core import CardFactory, TurnContext, MessageFactory
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema import CardAction, HeroCard, Mention, ConversationParameters, Attachment, Activity
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount, CacheInfo
from botbuilder.schema._connector_client_enums import ActionTypes
from config import DefaultConfig

CONFIG = DefaultConfig()

ADAPTIVECARDTEMPLATE = "resources/UserMentionCardTemplate.json"
ADAPTIVECARDTEMPLATEAVAYA = "resources/AvayaTemplate.json"

class TeamsConversationBot(TeamsActivityHandler):
    def __init__(self, app_id: str, app_password: str):
        self._app_id = app_id
        self._app_password = app_password

    async def on_teams_members_added(  # pylint: disable=unused-argument
        self,
        teams_members_added: [TeamsChannelAccount],
        team_info: TeamInfo,
        turn_context: TurnContext,
    ):
        for member in teams_members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Welcome to the team { member.given_name } { member.surname }. "
                )




    #Message Activity Event
    async def on_message_activity(self, turn_context: TurnContext):
        TurnContext.remove_recipient_mention(turn_context.activity)
        text = turn_context.activity.text.strip().lower()

        TurnContext.remove_recipient_mention(turn_context.activity)
        results = self.AzureSearch(text)
        await self._avaya_adaptive_card_activity(turn_context, results)
        return
        
    #Azure Search Api Call
    def AzureSearch(self, text):
        data= {"messages":[{"content":text,"role":"user"},]}
        baseUrl = CONFIG.BASE_URL
        response = requests.post(baseUrl, json=data)
        results = response.text
        return results

    async def _avaya_adaptive_card_activity(self, turn_context: TurnContext,data):
        card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATEAVAYA)
        with open(card_path, "rb") as in_file:
            template_json = json.load(in_file)

        promptData = json.loads(data)
        data = promptData["choices"][0]['message']
        dataIn = data["content"]

        for d in template_json["body"]:
            d["text"] = d["text"].replace("${data}", str(dataIn))

        adaptive_card_attachment = Activity(
             attachments=[CardFactory.adaptive_card(template_json)]
        )

        await turn_context.send_activity(adaptive_card_attachment)


    async def _mention_activity(self, turn_context: TurnContext):
        mention = Mention(
            mentioned=turn_context.activity.from_property,
            text=f"<at>{turn_context.activity.from_property.name}</at>",
            type="mention",
        )

        reply_activity = MessageFactory.text(f"Hello {mention.text}")
        reply_activity.entities = [Mention().deserialize(mention.serialize())]
        await turn_context.send_activity(reply_activity)








