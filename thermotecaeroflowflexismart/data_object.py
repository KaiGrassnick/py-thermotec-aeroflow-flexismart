"""Data Objects for the Python Thermotec AeroFlow® Library"""
from utils import create_current_temperature, calculate_temperature_from_int, calculate_temperature_offset_from_int


class Temperature:
    _current_temperature: float = 0.0
    _target_temperature: float = 0.0

    def __init__(self, data):
        self._set_data_from_array(data)

    def _set_data_from_array(self, data):
        self._current_temperature = create_current_temperature(int(data[0]), int(data[1]))
        self._target_temperature = calculate_temperature_from_int(int(data[2]))

    def get_current_temperature(self) -> float:
        return self._current_temperature

    def get_target_temperature(self) -> float:
        return self._target_temperature


class GatewayData:
    _firmware = "undefined"
    _installation_id = "undefined"
    _idu = "undefined"

    def __init__(self, data):
        self._set_data_from_array(data)

    def _set_data_from_array(self, data):
        self._firmware = data[0]
        self._installation_id = data[1]
        self._idu = data[2]

    def get_firmware(self):
        return self._firmware

    def get_installation_id(self):
        return self._installation_id

    def get_idu(self):
        return self._idu


class GatewayNetworkConfiguration:
    _ip: str = "0.0.0.0"
    _port: int = -1
    _gateway: str = "0.0.0.0"
    _subnet_mask: str = "0.0.0.0"
    _registration_server_ip: str = "0.0.0.0"
    _registration_server_port: int = -1

    def __init__(self, data):
        self._set_data_from_array(data)

    def _set_data_from_array(self, data):
        self._ip = f"{data[0]}.{data[1]}.{data[2]}.{data[3]}"
        self._port = int(f"{data[24]}{data[25]}")
        self._gateway = f"{data[4]}.{data[5]}.{data[6]}.{data[7]}"
        self._subnet_mask = f"{data[8]}.{data[9]}.{data[10]}.{data[11]}"
        self._registration_server_ip = f"{data[28]}.{data[29]}.{data[30]}.{data[31]}"
        self._registration_server_port = int(f"{data[32]}{data[33]}")

    def get_ip(self) -> str:
        return self._ip

    def get_port(self) -> int:
        return self._port

    def get_ip_with_port(self) -> str:
        return f"{self.get_ip()}:{self.get_port()}"

    def get_gateway(self) -> str:
        return self._gateway

    def get_subnet_mask(self) -> str:
        return self._subnet_mask

    def get_registration_server_ip(self) -> str:
        return self._registration_server_ip

    def get_registration_server_port(self) -> int:
        return self._registration_server_port

    def get_registration_server_ip_with_port(self) -> str:
        return f"{self.get_registration_server_ip()}:{self.get_registration_server_port()}"


class GatewayDateTime:
    _time: str = "00:00:00"
    _date: str = "00.00.0000"
    # _day_of_week: int = -1
    # _online: bool = False
    _ip: str = "undefined"
    _id: str = "00000"

    def __init__(self, data):
        self._set_data_from_array(data)

    def _set_data_from_array(self, data):
        self._time = f"{data[4].zfill(2)}:{data[5].zfill(2)}:{data[6].zfill(2)}"
        # self._day_of_week = int(data[3])  # should be calculated by date.
        self._date = f"{data[0].zfill(2)}.{data[1].zfill(2)}.20{data[2].zfill(2)}"  # works this way till 2099 :D
        # self._online = bool(data[7])  # not sure if this is online flag or something else
        self._ip = data[8]
        self._id = data[9]

    def get_time(self) -> str:
        return self._time

    def get_date(self) -> str:
        return self._date

    def get_ip(self) -> str:
        return self._ip

    def get_id(self) -> str:
        return self._id


class ModuleData:
    _current_temperature: float = 0.0
    _target_temperature: float = 0.0
    _time: str = "00:00:00"
    _programing: int = 0
    _programing2: int = 0
    _boost: int = 0
    _temperature_offset: float = 0.0
    _smart_start: int = 0
    _window_open_detection: int = 0
    _language: int = 0
    _id0 = "undefined"
    _id1 = "undefined"
    _id2 = "undefined"
    _id3 = "undefined"
    _fw_version: str = "undefined"

    def __init__(self, data):
        self._set_data_from_array(data)

    def _set_data_from_array(self, data):
        self._current_temperature = create_current_temperature(int(data[0]), int(data[1]))
        self._target_temperature = calculate_temperature_from_int(int(data[2]))
        self._time = f"{data[3].zfill(2)}:{data[4].zfill(2)}:{data[5].zfill(2)}"
        self._programing = int(data[7])  # 11 = one ? , 253 = off
        self._programing2 = int(data[8])  # save count? version?
        self._boost = int(data[9])  # 0 = off, >0 = on  | 4 = <5min, 12 = < 10 min, 20 = < 15 min, 28 = < 20 | 36 = < 25
        self._temperature_offset = calculate_temperature_offset_from_int(int(data[10]))
        self._smart_start = int(data[11])
        self._window_open_detection = int(data[12])
        self._language = int(data[13])  # 128 English, 129 German
        self._id0 = data[15]
        self._id1 = data[16]
        self._id2 = data[17]
        self._id3 = data[18]
        self._fw_version = data[19]

    def get_current_temperature(self) -> float:
        return self._current_temperature

    def get_target_temperature(self) -> float:
        return self._target_temperature

    def get_time(self) -> str:
        return self._time

    def get_programming_string(self) -> str:
        # programing = # 11 = one ? , 253 = off
        # programing2 = save count or version ?
        return f"{self._programing},{self._programing2}"

    def get_boost_time_left(self) -> int:
        boost_time_raw = self._boost

        time_left = 0
        if boost_time_raw > 0:
            time_left = round(boost_time_raw / 8) * 5

        return time_left

    def get_boost_time_left_string(self) -> str:
        time_left = self.get_boost_time_left()
        return f"< {time_left} min."

    def is_boost_active(self) -> bool:
        return self._boost > 0

    def get_temperature_offset(self) -> float:
        return self._temperature_offset

    def is_smart_start_enabled(self) -> bool:
        return self._smart_start == 1

    def is_window_open_detection_enabled(self) -> bool:
        return self._window_open_detection == 1

    def get_language(self) -> str:
        value = self._language
        language = "English"
        if value == 128:
            language = "Deutsch"

        return language

    def get_firmware_version(self) -> str:
        return self._fw_version
