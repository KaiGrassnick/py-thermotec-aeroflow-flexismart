from asyncio import run
from thermotecaeroflowflexismart.client import Client
import logging

logging.basicConfig(level=logging.DEBUG)


async def ping():
    gateway = Client("127.0.0.1")
    print(await gateway.ping())  # if gateway is available, response will be: True

run(ping())
