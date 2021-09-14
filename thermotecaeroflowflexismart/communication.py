"""Communication module for the Python Thermotec AeroFlow® Library"""
from asyncio import wait_for, exceptions, sleep
from asyncio_dgram import connect
from .exception import RequestTimeout


class FlexiSmartGateway:
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
        response = "UNEXPECTED_ERROR"
        try:
            # wait 100ms before every request
            await sleep(0.1)
            response = await wait_for(task, timeout)
        except exceptions.TimeoutError:
            raise RequestTimeout
        finally:
            # print("Message: {}, Response: {}".format(message, response))
            return response
