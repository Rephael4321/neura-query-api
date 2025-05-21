import asyncio
import json
from aiokafka import AIOKafkaConsumer
from config_log import logger
from config import ENVIRONMENT
from RequestsManager import RequestsManager
from ServerManager import ServerManager

requestsManager = RequestsManager()
serverManager = ServerManager()

topics = ["sign_up", "sign_in", "connect_db", "query_db", "query_ai"]


async def main():
    logger.info(f"MANAGER RUNNING ON '{ENVIRONMENT}' ENVIRONMENT.")
    
    async with AIOKafkaConsumer(
        *topics,
        bootstrap_servers="kafka:9092",
        auto_offset_reset="earliest",
        group_id="log-reader",
        value_deserializer = lambda v: json.loads(v.decode("utf-8"))
    ) as consumer:

        async for message in consumer:
            if message.topic == "sign_up":
                record_id, password = message.value.values()
                await serverManager.signUp(record_id, password)
            elif message.topic == "sign_in":
                record_id, password = message.value.values()
                await serverManager.signIn(record_id, password)
            elif message.topic == "connect_db":
                record_id, = message.value.values()
                await serverManager.connectDB(record_id)
            elif message.topic == "query_db":
                record_id, = message.value.values()
                await serverManager.queryDB(record_id)
            elif message.topic == "query_ai":
                record_id, = message.value.values()
                await serverManager.queryAI(record_id)


if __name__ == "__main__":
    asyncio.run(main())
