from openai import AsyncOpenAI
from ai.prompts import route_user_query_prompt, query_db_prompt, query_ai_prompt, query_none_prompt
from ai.Responders import Responders
from config_log import logger
import ast

class AI():
    def __init__(self):
        self.ai_client = AsyncOpenAI()
        self.model = "gpt-4o-mini"

    def _setUserQueryObject(self, query: str) -> dict:
        return { "role": "user", "content": query }

    async def _test_response(self):
        ai_response = await self.ai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": "Hello!"}]
        )

        response = ai_response
        print("AI Response Type:")
        print(type(response))
        print("AI Response:")
        print(response)
        print()
        
        message = response.choices[0].message.content
        print("AI Message Type:")
        print(type(message))
        print("AI Message:")
        print(message)

    async def route_user_query(self, metadata: list[str], db_provider: str, query: str) -> dict:
        while True:
            ai_response = await self.ai_client.chat.completions.create(
                model=self.model,
                messages=[
                    route_user_query_prompt(metadata, db_provider),
                    self._setUserQueryObject(query)
                ]
            )
            response = ai_response.choices[0].message.content
            response = response.replace("\n", " ")

            try:
                response = ast.literal_eval(response)
            except Exception as e:
                logger.error("Error from AI module, route_user_query method:")
                logger.error("Can't evaluate dict from response!")
                logger.error(f"Response: {response}")
            
            if response["responder"].upper() == Responders.DB.name:
                response = await self.query_db(metadata, db_provider, query)
            elif response["responder"].upper() == Responders.AI.name:
                response = await self.query_ai(metadata, db_provider, query)
            elif response["responder"].upper() == Responders.NONE.name:
                response = await self.query_none(metadata, db_provider, query)
            else:
                logger.error("Error from AI module:")
                logger.error("Responder out of scope!")
                logger.error(f"Responder: {response["responder"]}. (Responder scope is defined by Responders enum)")

            return response

    async def query_db(self, metadata: list[str], db_provider: str, query: str) -> dict:
        ai_response = await self.ai_client.chat.completions.create(
            model=self.model,
            messages=[
                query_db_prompt(metadata, db_provider),
                self._setUserQueryObject(query)
            ]
        )
        command = ai_response.choices[0].message.content
        command = command.replace("\n", " ")
        response = { "responder": "DB", "content": command}
        return response

    async def query_ai(self, metadata: list[str], db_provider: str, query: str) -> dict:
        ai_response = await self.ai_client.chat.completions.create(
            model=self.model,
            messages=[
                query_ai_prompt(metadata, db_provider),
                self._setUserQueryObject(query)
            ]
        )

        content = ai_response.choices[0].message.content
        content = content.replace("\n", " ")
        response = { "responder": "AI", "content": content}
        return response

    async def query_none(self, metadata: list[str], db_provider: str, query: str) -> dict:
        ai_response = await self.ai_client.chat.completions.create(
            model=self.model,
            messages=[
                query_none_prompt(metadata, db_provider),
                self._setUserQueryObject(query)
            ]
        )

        content = ai_response.choices[0].message.content
        content = content.replace("\n", " ")
        response = { "responder": "NONE", "content": content}
        return response
