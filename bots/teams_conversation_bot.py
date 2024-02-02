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
from botbuilder.schema import (
    CardAction,
    HeroCard,
    Mention,
    ConversationParameters,
    Attachment,
    Activity,
)
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount, CacheInfo
from botbuilder.schema._connector_client_enums import ActionTypes
from config import DefaultConfig
import json
import logging as log

from models.promptRatingResponse import PromptRatingResponse

CONFIG = DefaultConfig()

ADAPTIVECARDTEMPLATE = "resources/UserMentionCardTemplate.json"
ADAPTIVECARDTEMPLATEAVAYA = "resources/AvayaTemplate.json"
ADAPTIVECARDTEMPLATEANSWER = "resources/adaptiveCardAnswer.json"
ADAPTIVECARDTEMPLATEQUESTION = "resources/adaptiveCardQuestion.json"
MEMEBEREMAIL = "memberEmail"

log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)


class TeamsConversationBot(TeamsActivityHandler):
    def __init__(self, app_id: str, app_password: str):
        self._app_id = app_id
        self._app_password = app_password
        self.RESULTS = ""
        self.email = ""
        self.messages = [{
                    "content": "I'm sorry, but I couldn't find any specific information related to the question you asked.",
                    "role": "assistant",
                }]

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

    # Message Activity Event
    async def on_message_activity(self, turn_context: TurnContext):
        TurnContext.remove_recipient_mention(turn_context.activity)

        if turn_context.activity.text != None:
            text = turn_context.activity.text.strip().lower()
            log.info("===HEADER================D E B U G 010")

            member_email = await self.get_member(turn_context)
            self.email = member_email
            TurnContext.remove_recipient_mention(turn_context.activity)
            #Search question to API endpoint
            results = self.AzureSearch(text, member_email)
            #Get answer from results and add to messages history
            answer = self.GetAnswer(results)
            self.messages.append({"content": answer, "role": "assistant"})
            #Build adaptive card with answer
            await self._avaya_adaptive_answer_card(turn_context, results)


            # await self._avaya_adaptive_card_activity(turn_context, results)
        else:
            if self.RESULTS != "":
                self.messages = [{
                    "content": "I'm sorry, but I couldn't find any specific information related to the question you asked.",
                    "role": "assistant",
                }]
                rating =   await self.response_rating(turn_context, self.email)
                results = self.send_rating(rating)
                if results:

                   await turn_context.send_activity(
                       f"You said your answer was: '{ turn_context.activity.value['OverallRating'] }'"
                   )
            else:
                await turn_context.send_activity(
                    f"You have already rated this answer"
                )

                return




    def GetAnswer(self, results):
        self.RESULTS = results
        responseData = json.loads(results)
        message = responseData["choices"][0]["message"]
        answer = message["content"]
        return answer

    async def response_rating(self, turn_context, email):
        # Rating
        action = turn_context.activity.value
        rating = action["OverallRating"]
        print(action["OverallRating"])
        # Answer and Question
        responseData = json.loads(self.RESULTS)
        # Question
        choice = responseData["choices"][0]["context"]
        thoughts = choice["thoughts"][0]
        question = thoughts["description"]
        # Answer
        message = responseData["choices"][0]["message"]
        answer = message["content"]
        responseRatingData = PromptRatingResponse(
            "persona",
            question,
            "addtext",
            "out_text_rd",
            answer,
            rating,
            "user_rating_comments",
            email,
        )
        rating = responseRatingData
        self.email = ""
        self.RESULTS = ""

        return rating

    async def get_member(self, turn_context):
        member = await TeamsInfo.get_member(
            turn_context, turn_context.activity.from_property.id
        )
        member_email = member.email
        if member_email == None:
            member_email = "test.email@test.com"
        log.info(member_email)
        return member_email

    # Azure Search Api Call
    def AzureSearch(self, text, email):


        self.messages.append({"content": text, "role": "user"})
        request = {
            "messages": self.messages,
            "stream": False,
            "context": {
                "overrides": {
                    "top": 3,
                    "retrieval_mode": "hybrid",
                    "semantic_ranker": True,
                    "semantic_captions": False,
                    "suggest_followup_questions": False,
                    "use_oid_security_filter": False,
                    "use_groups_security_filter": False,
                    "vector_fields": ["embedding"],
                    "use_gpt4v": False,
                    "gpt4v_input": "textAndImages",
                }
            },
            "session_state": None,
            "email": email,
        }
        data = {
            "messages": [
                {"content": text, "role": "user"},
            ],
            "email": email,
        }
        baseUrl = CONFIG.BASE_URL
        response = requests.post(baseUrl, json=request)
        results = response.text
        return results

    def send_rating(self, rating):
        ratingout = {
        "Prompt_Persona" : rating.Prompt_Persona,
        "Prompt_Question" : rating.Prompt_Question,
        "Prompt_AddText" : rating.Prompt_AddText,
        "RelevantDocumentsText" : rating.RelevantDocumentsText,
        "retAnswer" : rating.retAnswer,
        "userRatingRadio" : rating.userRatingRadio,
        "userRatingComments" : rating.userRatingComments,
        "comments" : rating.comments,
        "user_email" : rating.user_email


        }
        baseUrl = CONFIG.RATINGS_URL
        response = requests.post(baseUrl, json=ratingout)
        results = response.text
        return results

    async def _avaya_adaptive_answer_card(self, turn_context: TurnContext, data):
        card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATEANSWER)
        with open(card_path, "rb") as in_file:
            template_json = json.load(in_file)

        promptData = json.loads(data)
        data = promptData["choices"][0]["message"]
        dataIn = data["content"]

        d = template_json["body"]
        i = d[2]["items"]
        d = i[2]
        r = d
        r["text"] = r["text"].replace("${data}", str(dataIn))

        adaptive_card_attachment = Activity(
            attachments=[CardFactory.adaptive_card(template_json)]
        )

        await turn_context.send_activity(adaptive_card_attachment)


    async def _avaya_adaptive_question_card(self, turn_context: TurnContext):
        card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATEQUESTION)
        with open(card_path, "rb") as in_file:
            template_json = json.load(in_file)

        adaptive_card_attachment = Activity(
            attachments=[CardFactory.adaptive_card(template_json)]
        )
        await turn_context.send_activity(adaptive_card_attachment)
    async def _avaya_adaptive_card_activity(self, turn_context: TurnContext, data):
        card_path = os.path.join(os.getcwd(), ADAPTIVECARDTEMPLATEAVAYA)
        with open(card_path, "rb") as in_file:
            template_json = json.load(in_file)

        promptData = json.loads(data)
        data = promptData["choices"][0]["message"]
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
