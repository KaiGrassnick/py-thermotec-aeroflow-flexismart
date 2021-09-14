from asyncio import run
from thermotecaeroflowflexismart.client import Client


async def ping():
    gateway = Client("127.0.0.1")
    print(await gateway.ping())


if __name__ == "ping":
    run(ping())
