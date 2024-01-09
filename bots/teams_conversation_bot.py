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
from botbuilder.core.teams import TeamsActivityHandler, TeamsInfo
from botbuilder.schema import CardAction, HeroCard, Mention, ConversationParameters, Attachment, Activity
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount
from botbuilder.schema._connector_client_enums import ActionTypes

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

    async def on_message_activity(self, turn_context: TurnContext):
        TurnContext.remove_recipient_mention(turn_context.activity)
        text = turn_context.activity.text.strip().lower()

        data= {"messages":[{"content":text,"role":"user"},]}


        baseUrl = "https://app-backend-h4fafkwv3yuq4.azurewebsites.net/chat"

        x = requests.post(baseUrl, json=data)

        res = x.text

        await self._avaya_adaptive_card_activity(turn_context, res)
        return

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



