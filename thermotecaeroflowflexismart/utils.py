"""Util functions for the Python Thermotec AeroFlow® Library"""
from exception import InvalidModule


def calculate_temperature_from_int(value: int) -> float:
    if value > 128:
        return (value - 128) + 0.5

    return float(value)


def calculate_int_from_temperature(temperature: float) -> int:
    int_response = int(temperature)
    if temperature % 1 != 0:
        int_response = 128 + int_response

    return int_response


# 0 = 0, 10 = 1,0, -1,0 = 246
def calculate_temperature_offset_from_int(value: int) -> float:
    # example: value 157 represents -99 which results in -9,9°C
    # there might be a better way to calculate this, but it works for now
    if value >= 128:
        value = value - 256

    return float(value / 10)


# 0 = 0, 10 = 1,0, -1,0 = 246
def calculate_int_from_temperature_offset(temperature: float) -> int:
    value = int(temperature * 10)
    if value < 0:
        value = 256 - (value * -1)

    return value


def create_current_temperature(main_value: int, second_value: int) -> float:
    return float(f"{main_value}.{second_value}")


def check_if_zone_exists(zones, zone) -> None:
    if len(zones) == 0:
        raise Exception(f"Zone out of range. No existing zones")

    if zone <= 0 or zone > len(zones):
        min_zone = 1
        max_zone = len(zones)
        raise Exception(f"Zone out of range. Expected: {min_zone} - {max_zone}. Given: {zone}")


def check_if_module_is_valid(module_count: int, module_id: int) -> None:
    if module_id > module_count:
        raise InvalidModule(f"Module with id: {module_id} does not exist in given zone. Max module id: {module_count}")

    return None
