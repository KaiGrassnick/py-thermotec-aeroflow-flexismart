"""Client module for the Python Thermotec AeroFlow® Library"""
from .utils import (
    check_if_zone_exists,
    check_if_module_is_valid,
    calculate_int_from_temperature,
    calculate_temperature_offset_from_int,
    calculate_int_from_temperature_offset
)

from datetime import datetime
from .communication import FlexiSmartGateway
from .exception import InvalidResponse, InvalidRequest, RequestTimeout
from .const import OPERATION, OPERATION_OK, OKAY

from .data_object import (
    GatewayNetworkConfiguration,
    Temperature,
    GatewayData,
    GatewayDateTime,
    ModuleData
)


class Client:
    def __init__(self, host: str, port: int = 6653):
        self._gateway = FlexiSmartGateway(host, port)

    # Command: PING
    # GatewayResponse: OP
    async def ping(self) -> bool:
        command = "PING"

        try:
            response = await self._gateway.send_message_get_response(command)

            if not response.startswith(OPERATION):
                raise InvalidResponse()

            return True
        except RequestTimeout:
            return False
        finally:
            return False

    # Command: OPH...
    # GatewayResponse: OPOK,<>
    async def get_date_time(self) -> GatewayDateTime:
        operation = "OPH"
        command = f"{operation}/"
        response = await self._gateway.send_message_get_response(command)

        status = OPERATION_OK
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        data = response.replace(response_identifier, "").split(",")
        return GatewayDateTime(data)

    async def update_date_time(self) -> None:
        now = datetime.now()
        return await self.set_date_time(now)

    # Command: OPF...
    # GatewayResponse: OPOK
    async def set_date_time(self, target_datetime: datetime) -> None:
        hour = "%H"
        minute = "%M"
        second = "%S"
        day_of_week = target_datetime.weekday()  # Sunday = 6 - Monday = 0
        day = "%d"
        month = "%m"
        year = "%y"

        operation = "OPF"
        command = target_datetime.strftime(f"{operation}{hour}{minute}{second}{day_of_week}/{day},{month},{year}/")

        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OPERATION_OK):
            raise InvalidResponse()

        return None

    # Command: OPF/
    # GatewayResponse: OPOK,<firmware_version>,<installation_id>,<idu>
    async def get_gateway_data(self) -> GatewayData:
        operation = "OPF"
        command = f"{operation}/"
        response = await self._gateway.send_message_get_response(command)

        status = OPERATION_OK
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        data = response.replace(response_identifier, "").split(",")
        return GatewayData(data)

    # Command: OPS1/
    # GatewayResponse: OPOK,OPS1,<server_sync_id>,x,x,x,x,<id_a>,<id_b>,x,x,x
    # if sync id != last sync id -> environment has changed
    async def get_status(self):
        operation = "OPS1"
        command = f"{operation}/"
        response = await self._gateway.send_message_get_response(command)

        status = OPERATION_OK
        response_identifier = f"{status},{operation},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        data = response.replace(response_identifier, "").split(",")
        return {"serverSyncId": data[0], "idA": data[5], "idB": data[6]}

    # Command: OPS2/
    # GatewayResponse: OPOK,OPS2,<zone_id>,<...>
    async def get_zones(self):
        operation = "OPS2"
        command = f"{operation}/"
        response = await self._gateway.send_message_get_response(command)

        status = OPERATION_OK
        response_identifier = f"{status},{operation},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        zones = []
        data = response.replace(response_identifier, "").split(",")
        for value in data:
            zones.append(int(value))

        return zones

    # Command: OPS3/
    # GatewayResponse: OPOK,OPS3,<module_count>,<...>
    async def get_zones_with_module_count(self) -> [int]:
        operation = "OPS3"
        command = f"{operation}/"
        response = await self._gateway.send_message_get_response(command)

        status = OPERATION_OK
        response_identifier = f"{status},{operation},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        zones = []
        data = response.replace(response_identifier, "").split(",")
        for value in data:
            zones.append(int(value))

        return zones

    # Command: OPS4/
    # GatewayResponse: OPOK,OPS4,<x>,<x>,<x>
    # async def get_ops4(self):
    #     operation = "OPS4"
    #     command = f"{operation}/"
    #     response = await self._gateway.send_message_get_response(command)
    #
    #     status = OPERATION_OK
    #     response_identifier = f"{status},{operation},"
    #
    #     placeholder = []
    #     if response.startswith(response_identifier):
    #         placeholder = response.replace(response_identifier, "").split(",")
    #
    #     return placeholder

    # Command: OPS5/
    # GatewayResponse: OPOK,OPS5,<x>,<x>,<x>
    # async def get_ops5(self):
    #     operation = "OPS5"
    #     command = f"{operation}/"
    #     response = await self._gateway.send_message_get_response(command)
    #
    #     status = OPERATION_OK
    #     response_identifier = f"{status},{operation},"
    #
    #     placeholder = []
    #     if response.startswith(response_identifier):
    #         placeholder = response.replace(response_identifier, "").split(",")
    #
    #     return placeholder

    # Command: OPS6/
    # GatewayResponse: OPOK,OPS6
    # async def get_ops6(self):
    #     operation = "OPS6"
    #     command = f"{operation}/"
    #     response = await self._gateway.send_message_get_response(command)
    #
    #     status = OPERATION_OK
    #     response_identifier = f"{status},{operation},"
    #
    #     placeholder = []
    #     if response.startswith(response_identifier):
    #         placeholder = response.replace(response_identifier, "").split(",")
    #
    #     return placeholder

    # Command: OPS7/
    # GatewayResponse: OPOK,OPS7
    # async def get_ops7(self):
    #     operation = "OPS7"
    #     command = f"{operation}/"
    #     response = await self._gateway.send_message_get_response(command)
    #
    #     status = OPERATION_OK
    #     response_identifier = f"{status},{operation},"
    #
    #     placeholder = []
    #     if response.startswith(response_identifier):
    #         placeholder = response.replace(response_identifier, "").split(",")
    #
    #     return placeholder

    # Command: OPS38/
    # GatewayResponse: OPOK,OPS38,<ip[0-3]>,<gateway[4-7]>,<netmask[8-11],x,x,x,x
    async def get_network_configuration(self) -> GatewayNetworkConfiguration:
        operation = "OPS38"
        command = f"{operation}/"
        response = await self._gateway.send_message_get_response(command)

        status = OPERATION_OK
        response_identifier = f"{status},{operation},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        data = response.replace(response_identifier, "").split(",")
        return GatewayNetworkConfiguration(data)

    # Command: OPS43/
    # GatewayResponse: OPOK,OPS43,<x>,<x>
    # async def get_ops43(self):
    #     operation = "OPS43"
    #     command = f"{operation}/"
    #     response = await self._gateway.send_message_get_response(command)
    #
    #     status = OPERATION_OK
    #     response_identifier = f"{status},{operation},"
    #
    #     placeholder = []
    #     if response.startswith(response_identifier):
    #         placeholder = response.replace(response_identifier, "").split(",")
    #
    #     return placeholder

    async def register_module_in_zone(self, zone: int, timeout: int = 30) -> None:
        return await self._register_module(zone, timeout)

    # Command: OPMW<zone_position>,<zone_id>/
    # GatewayResponse: OPOK
    async def create_zone(self) -> None:
        zones = await self.get_zones_with_module_count()

        total_zones = len(zones)

        zone_position = total_zones + 9
        new_zone_id = total_zones + 1

        operation = "OPMW"
        command = f"{operation}{zone_position},{new_zone_id}/"
        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OPERATION_OK):
            raise InvalidResponse

        return None

    # Command: OPMW<big_zone_id>,0/
    # GatewayResponse: OPOK
    async def delete_zone(self, zone: int) -> None:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        # module type = 120
        # some crazy constant value = 8
        # zone id = <zone>
        big_zone_id = 120 + 8 + zone

        operation = "OPMW"
        command = f"{operation}{big_zone_id},0/"
        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OPERATION_OK):
            raise InvalidResponse

        return None

    # Command: R#<zone_id>#<zone_module_count>#0#0*?F/
    async def get_module_data(self, zone: int, module: int) -> ModuleData:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "R"
        command = f"{operation}#{zone}#{module}#0#0*?F/"
        response = await self._gateway.send_message_get_response(command)

        status = OKAY
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        data = response.replace(response_identifier, "").split(",")
        return ModuleData(data)

    # >>>>>>> Temperature <<<<<<< #
    async def get_zone_temperature(self, zone: int) -> Temperature:
        return await self._get_temperature(zone)

    async def set_zone_temperature(self, zone: int, temperature: float) -> None:
        return await self._set_temperature(temperature, zone)

    async def get_module_temperature(self, zone: int, module: int) -> Temperature:
        return await self._get_temperature(zone, module)

    async def set_module_temperature(self, zone: int, module: int, temperature: float) -> None:
        return await self._set_temperature(temperature, zone, module)

    # >>>>>>> Offset Temperature <<<<<<< #
    async def get_zone_temperature_offset(self, zone: int) -> float:
        return await self._get_temperature_offset(zone)

    async def set_zone_temperature_offset(self, zone: int, temperature: float) -> None:
        return await self._set_temperature_offset(temperature, zone)

    async def get_module_temperature_offset(self, zone: int, module: int) -> float:
        return await self._get_temperature_offset(zone, module)

    async def set_module_temperature_offset(self, zone: int, module: int, temperature: float) -> None:
        return await self._set_temperature_offset(temperature, zone, module)

    # >>>>>>> Anti Freeze Temperature <<<<<<< #
    async def get_zone_anti_freeze_temperature(self, zone: int) -> float:
        return await self._get_anti_freeze_temperature(zone)

    async def set_zone_anti_freeze_temperature(self, zone: int, temperature: float) -> None:
        return await self._set_anti_freeze_temperature(temperature, zone)

    async def get_module_anti_freeze_temperature(self, zone: int, module: int) -> float:
        return await self._get_anti_freeze_temperature(zone, module)

    async def set_module_anti_freeze_temperature(self, zone: int, module: int, temperature: float) -> None:
        return await self._set_anti_freeze_temperature(temperature, zone, module)

    # >>>>>>> Boost <<<<<<< #
    async def get_zone_boost(self, zone: int) -> float:
        return await self._get_boost(zone)

    async def set_zone_boost(self, zone: int, time: int) -> None:
        return await self._set_boost(time, zone)

    async def get_module_boost(self, zone: int, module: int) -> int:
        return await self._get_boost(zone, module)

    async def set_module_boost(self, zone: int, module: int, time: int) -> None:
        return await self._set_boost(time, zone, module)

    # >>>>>>> Window Open Detection <<<<<<< #
    async def is_zone_window_open_detection_enabled(self, zone: int) -> bool:
        return await self._is_window_open_detection_enabled(zone)

    async def enable_zone_window_open_detection(self, zone: int) -> None:
        return await self._set_window_open_detection(True, zone)

    async def disable_zone_window_open_detection(self, zone: int) -> None:
        return await self._set_window_open_detection(False, zone)

    async def set_zone_window_open_detection(self, zone: int, value: bool) -> None:
        return await self._set_window_open_detection(value, zone)

    async def is_module_window_open_detection_enabled(self, zone: int, module: int) -> bool:
        return await self._is_window_open_detection_enabled(zone, module)

    async def enable_module_window_open_detection(self, zone: int, module: int) -> None:
        return await self._set_window_open_detection(True, zone, module)

    async def disable_module_window_open_detection(self, zone: int, module: int) -> None:
        return await self._set_window_open_detection(False, zone, module)

    async def set_module_window_open_detection(self, zone: int, module: int, value: bool) -> None:
        return await self._set_window_open_detection(value, zone, module)

    # >>>>>>> Smart Start <<<<<<< #
    async def is_zone_smart_start_enabled(self, zone: int) -> bool:
        return await self._is_smart_start_enabled(zone)

    async def enable_zone_smart_start(self, zone: int) -> None:
        return await self._set_smart_start(True, zone)

    async def disable_zone_smart_start(self, zone: int) -> None:
        return await self._set_smart_start(False, zone)

    async def set_zone_smart_start(self, zone: int, value: bool) -> None:
        return await self._set_smart_start(value, zone)

    async def is_module_smart_start_enabled(self, zone: int, module: int) -> bool:
        return await self._is_smart_start_enabled(zone, module)

    async def enable_module_smart_start(self, zone: int, module: int) -> None:
        return await self._set_smart_start(True, zone, module)

    async def disable_module_smart_start(self, zone: int, module: int) -> None:
        return await self._set_smart_start(False, zone, module)

    async def set_module_smart_start(self, zone: int, module: int, value: bool) -> None:
        return await self._set_smart_start(value, zone, module)

    # >>>>>>> Holiday <<<<<<< #
    # TODO: Implement Holiday feature

    # >>>>>>> Programming <<<<<<< #
    # TODO: Implement Programming feature

    # >>>>>>> Restart <<<<<<< #
    async def restart_zone(self, zone: int) -> ModuleData:
        # if we restart multiple we might get ER,1 but it still works
        return await self._restart_module(zone)

    async def restart_module(self, zone: int, module: int) -> ModuleData:
        return await self._restart_module(zone, module)

    # --------------------------------- #
    # >>>>>>> Private functions <<<<<<< #
    # --------------------------------- #

    # Command: OPZI199,<zone>,<module>/
    # GatewayResponse: OPOK
    async def _register_module(self, zone: int, timeout: int, module: int = -1) -> None:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            target_module = module

        operation = "OPZI199"
        command = f"{operation},{zone},{target_module}/"
        response = await self._gateway.send_message_get_response(command, timeout)

        status = OPERATION_OK
        response_identifier = f"{status}"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        return None

    # Command: D<zone_id>#<zone_module_count>#0#0*?T/
    # GatewayResponse: OK,<current_temperature>,<current_temperature>,<target_temperature>
    async def _get_temperature(self, zone: int, module: int = -1) -> Temperature:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        command = f"{operation}#{zone}#{target_module}#0#0*?T/"
        response = await self._gateway.send_message_get_response(command)

        status = OKAY
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        data = response.replace(response_identifier, "").split(",")
        return Temperature(data)

    # Command: D<zone_id>#<zone_module_count>#0#0*T<target_temperature>/
    # GatewayResponse: OK
    async def _set_temperature(self, temperature: float, zone: int, module: int = -1) -> None:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        target_temperature = calculate_int_from_temperature(temperature)

        command = f"{operation}#{zone}#{target_module}#0#0*T{target_temperature}/"
        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OKAY):
            raise InvalidResponse()

        return None

    # Command: R<zone_id>#<zone_module_count>#0#0*?E#0#9/
    # GatewayResponse: OK
    async def _get_temperature_offset(self, zone: int, module: int = -1) -> float:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        command = f"{operation}#{zone}#{target_module}#0#0*?E#0#9/"
        response = await self._gateway.send_message_get_response(command)

        status = OKAY
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        data = response.replace(response_identifier, "").split(",")
        return calculate_temperature_offset_from_int(int(data[0]))

    # Command: R<zone_id>#<zone_module_count>#0#0*SEP#0#9#<target_offset_temperature>/
    # GatewayResponse: OK
    async def _set_temperature_offset(self, temperature: float, zone: int, module: int = -1) -> None:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        target_temperature = calculate_int_from_temperature_offset(temperature)

        command = f"{operation}#{zone}#{target_module}#0#0*SEP#0#9#{target_temperature}/"
        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OKAY):
            raise InvalidResponse()

        return None

    # Command: D<zone_id>#<zone_module_count>#0#0*?E#1#20/
    # GatewayResponse: OK
    async def _get_anti_freeze_temperature(self, zone: int, module: int = -1) -> float:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        command = f"{operation}#{zone}#{target_module}#0#0*?E#1#20/"
        response = await self._gateway.send_message_get_response(command)

        status = OKAY
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse

        data = int(response.replace(response_identifier, ""))

        # if data == 255 -> Anti Freeze was never Set -> default might be 5°C
        if data == 255:
            data = 5

        return float(data)

    # Command: D<zone_id>#<zone_module_count>#0#0*SEP#1#20#<target_temperature>/
    # GatewayResponse: OK
    async def _set_anti_freeze_temperature(self, temperature: float, zone: int, module: int = -1) -> None:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        target_temperature = int(temperature)

        command = f"{operation}#{zone}#{target_module}#0#0*SEP#1#20#{target_temperature}/"
        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OKAY):
            raise InvalidResponse()

        return None

    # Command: D<zone_id>#<zone_module_count>#0#0*?E#1#20/
    # GatewayResponse: OK
    async def _get_boost(self, zone: int, module: int = -1) -> int:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        command = f"{operation}#{zone}#{target_module}#0#0*?E#1#22/"
        response = await self._gateway.send_message_get_response(command)

        status = OKAY
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse

        data = int(response.replace(response_identifier, ""))

        if data == 255:
            data = 0

        # Multiply by 5 as each step is 5 minutes
        return data * 5

    # Command: D<zone_id>#<zone_module_count>#0#0*SEP#1#22#<target_temperature>/
    # GatewayResponse: OK
    async def _set_boost(self, time: int, zone: int, module: int = -1) -> None:
        if time > 95:
            raise InvalidRequest("Boost time can not exceed 95 Minutes")

        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        target_time = 0
        if time >= 5:
            target_time = int(time / 5)

        command = f"{operation}#{zone}#{target_module}#0#0*SEP#1#22#{target_time}/"
        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OKAY):
            raise InvalidResponse()

        return None

    # Command: D<zone_id>#<zone_module_count>#0#0*?E#0#6/
    # GatewayResponse: OK
    async def _is_window_open_detection_enabled(self, zone: int, module: int = -1) -> bool:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        command = f"{operation}#{zone}#{target_module}#0#0*?E#0#6/"
        response = await self._gateway.send_message_get_response(command)

        status = OKAY
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse

        return bool(int(response.replace(response_identifier, "")))

    # Command: D<zone_id>#<zone_module_count>#0#0*SEP#0#6#<target_temperature>/
    # GatewayResponse: OK
    async def _set_window_open_detection(self, value: bool, zone: int, module: int = -1) -> None:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        target_value = int(value)

        command = f"{operation}#{zone}#{target_module}#0#0*SEP#0#6#{target_value}/"
        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OKAY):
            raise InvalidResponse()

        return None

    # Command: D<zone_id>#<zone_module_count>#0#0*?E#0#7/
    # GatewayResponse: OK
    async def _is_smart_start_enabled(self, zone: int, module: int = -1) -> bool:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        command = f"{operation}#{zone}#{target_module}#0#0*?E#0#7/"
        response = await self._gateway.send_message_get_response(command)

        status = OKAY
        response_identifier = f"{status},"

        if not response.startswith(response_identifier):
            raise InvalidResponse

        return bool(int(response.replace(response_identifier, "")))

    # Command: D<zone_id>#<zone_module_count>#0#0*SEP#0#7#<target_temperature>/
    # GatewayResponse: OK
    async def _set_smart_start(self, value: bool, zone: int, module: int = -1) -> None:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        target_value = int(value)

        command = f"{operation}#{zone}#{target_module}#0#0*SEP#0#7#{target_value}/"
        response = await self._gateway.send_message_get_response(command)

        if not response.startswith(OKAY):
            raise InvalidResponse()

        return None

    # Command: D<zone_id><module>#0#0*-TU#0#0#0#0#2/
    # GatewayResponse: OPOK,<module-data>
    async def _restart_module(self, zone: int, module: int = -1) -> ModuleData:
        zones = await self.get_zones_with_module_count()

        check_if_zone_exists(zones, zone)

        operation = "D"
        target_module = zones[(zone - 1)]

        # if module was not -1 we verify the requested module
        if module != -1:
            check_if_module_is_valid(target_module, module)
            operation = "R"
            target_module = module

        # if we remove one 0 after TU, we reset the module (by accident?)
        command = f"{operation}#{zone}#{target_module}#0#0*-TU#0#0#0#0#2/"

        response = await self._gateway.send_message_get_response(command)

        response_identifier = f"{OKAY},"

        if not response.startswith(response_identifier):
            raise InvalidResponse()

        data = response.replace(response_identifier, "").split(",")
        return ModuleData(data)

# Update Temperature etc.:
# ER,2 = Communication error with one module (2 in this case)
# ER,1,2 = Communication error with two modules (1,2 in this case)
