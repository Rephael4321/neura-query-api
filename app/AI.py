from openai import AsyncOpenAI

class AI():
    def __init__(self):
        self.ai_client = AsyncOpenAI()

    async def query(self, metadata: list[str], db_provider: str, query: str) -> str:
        ai_response = await self.ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are helping me to create SQL and NoSQL queries."
                },
                {
                    "role": "system",
                    "content": f"Here is the metadata of my tables {str(metadata)}"
                },
                {
                    "role": "system",
                    "content": f"My DB provider is {db_provider}"
                },
                {
                    "role": "system",
                    "content": "I'm only allowed to ask how to generate queries for my db. If it is something else, you reject me!"
                },
                {
                    "role": "system",
                    "content": "If you can reply, you only reply the query. Nothing else! Write only the query, no extra marks around it!"
                },
                # {
                #     "role": "system",
                #     "content": "If you cannot generate a query, like for example, I'm asking to fetch users from a table that doesn't exist, you reply 'Error: No query supported'"
                # },
                # {
                #     "role": "system",
                #     "content": "If you can't reply at all, you reply 'Error: Non query generation related query'"
                # },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        response = ai_response.choices[0].message.content
        response = response.replace("\n", " ")
        return response
