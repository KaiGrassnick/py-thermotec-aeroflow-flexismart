"""Communication module for the Python Thermotec AeroFlow® Library"""
from random import randint

from asyncio import wait_for, exceptions, sleep

from asyncio_dgram import connect

from .exception import RequestTimeout


class FlexiSmartGateway:
    _running: bool = False

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    async def __send_message_get_response(self, message: str):
        # Create a client for the gateway
        client = await connect((self._host, self._port))

        # Send the encoded string to the desired gateway
        await client.send(str.encode(message))

        # (Hopefully) Get the response message from the gateway
        data, remote_addr = await client.recv()

        # Close socket manually after call to free the resources
        client.close()

        # Extract the message from the response and remove the null value at the end of the message
        response_message = data.rstrip(b'\x00')

        # Decode the message to a string and return
        return response_message.decode()

    async def send_message_get_response(self, message: str, timeout: int = 3):
        task = self.__send_message_get_response(message)
        try:
            force_execution_max_count = 30
            execution_attempt = 0
            while self._running:
                execution_attempt = execution_attempt + 1
                if execution_attempt > force_execution_max_count:
                    break

                wait_time = (randint(1, 5) / 10)
                await sleep(wait_time)

            self._running = True
            await sleep(0.1)
            response = await wait_for(task, timeout)
            # print("Message: {}, Response: {}".format(message, response))
            self._running = False
            return response
        except exceptions.TimeoutError:
            self._running = False
            raise RequestTimeout
        except Exception:
            self._running = False
            return "UNEXPECTED_ERROR"
