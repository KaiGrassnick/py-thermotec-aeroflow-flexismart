"""Custom Exceptions for the Python Thermotec AeroFlow® Library"""


class RequestTimeout(Exception):
    """Response was not received within specified timeframe"""


class InvalidResponse(Exception):
    """Response was not as expected"""


class InvalidModule(Exception):
    """Module does not exist in zone"""


class InvalidRequest(Exception):
    """Request was invalid"""
