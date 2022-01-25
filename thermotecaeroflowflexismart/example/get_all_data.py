from asyncio import run
from thermotecaeroflowflexismart.client import Client
import logging

logging.basicConfig(level=logging.WARNING)


async def ping():
    gateway = Client("127.0.0.1")
    module_all_data = await gateway.get_all_data()

    for key, data in module_all_data.items():
        print(data.get_zone_id())
        print(data.get_module_id())
        print(data.get_module_data().get_current_temperature())
        print(data.get_module_data().get_target_temperature())
        print(data.get_date_time().get_date_time_string())

run(ping())
