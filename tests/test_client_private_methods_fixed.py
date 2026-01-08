import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from tests.const import CLIENT_IP
from thermotecaeroflowflexismart.client import Client
from thermotecaeroflowflexismart.exception import InvalidResponse, InvalidRequest
from thermotecaeroflowflexismart.data_object import (
    Temperature,
    HolidayData, ModuleData,
)


class TestClientPrivateTemperatureMethods:
    """Tests for private temperature-related methods"""

    @pytest.mark.asyncio
    async def test_get_temperature_zone_success(self):
        """Test _get_temperature for zone retrieval"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,18,08,20"
            ]
        )

        result = await client._get_temperature(zone=1)
        assert isinstance(result, Temperature)
        assert result.get_current_temperature() == 18.8
        assert result.get_target_temperature() == 20.0
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?T/")

    @pytest.mark.asyncio
    async def test_get_temperature_module_success(self):
        """Test _get_temperature for module retrieval"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,18,08,20"
            ]
        )

        result = await client._get_temperature(zone=1, module=1)
        assert isinstance(result, Temperature)
        assert result.get_current_temperature() == 18.8
        assert result.get_target_temperature() == 20.0
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?T/")

    @pytest.mark.asyncio
    async def test_get_temperature_invalid_response(self):
        """Test _get_temperature with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )
        with pytest.raises(InvalidResponse):
            await client._get_temperature(zone=1)

    @pytest.mark.asyncio
    async def test_get_temperature_decimal_value(self):
        """Test _get_temperature with decimal temperature"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,20,05,129"
            ]
        )

        result = await client._get_temperature(zone=1)
        assert result.get_current_temperature() == 20.5
        assert result.get_target_temperature() == 1.5

    @pytest.mark.asyncio
    async def test_set_temperature_zone_success(self):
        """Test _set_temperature for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_temperature(temperature=22.5, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*T150/")

    @pytest.mark.asyncio
    async def test_set_temperature_module_success(self):
        """Test _set_temperature for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )
        
        await client._set_temperature(temperature=21.0, zone=1, module=1)
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*T21/")

    @pytest.mark.asyncio
    async def test_set_temperature_decimal_value(self):
        """Test _set_temperature with decimal temperature"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_temperature(temperature=21.5, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*T149/")

    @pytest.mark.asyncio
    async def test_set_temperature_invalid_response(self):
        """Test _set_temperature with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._set_temperature(temperature=22.0, zone=1)


class TestClientPrivateTemperatureOffsetMethods:
    """Tests for private temperature offset methods"""

    @pytest.mark.asyncio
    async def test_get_temperature_offset_zone(self):
        """Test _get_temperature_offset for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,10"
            ]
        )

        result = await client._get_temperature_offset(zone=1)
        assert result == 1.0
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?E#0#9/")

    @pytest.mark.asyncio
    async def test_get_temperature_offset_module(self):
        """Test _get_temperature_offset for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,10"
            ]
        )
        
        result = await client._get_temperature_offset(zone=1, module=1)
        assert result == 1.0
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?E#0#9/")

    @pytest.mark.asyncio
    async def test_get_temperature_offset_negative(self):
        """Test _get_temperature_offset with negative offset"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,246"
            ]
        )

        result = await client._get_temperature_offset(zone=1)
        assert result == -1.0

    @pytest.mark.asyncio
    async def test_get_temperature_offset_invalid_response(self):
        """Test _get_temperature_offset with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._get_temperature_offset(zone=1)

    @pytest.mark.asyncio
    async def test_set_temperature_offset_zone(self):
        """Test _set_temperature_offset for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_temperature_offset(temperature=1.5, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*SEP#0#9#15/")


    @pytest.mark.asyncio
    async def test_set_temperature_offset_module(self):
        """Test _set_temperature_offset for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )
        
        await client._set_temperature_offset(temperature=-1.0, zone=1, module=1)
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*SEP#0#9#246/")

    @pytest.mark.asyncio
    async def test_set_temperature_offset_invalid_response(self):
        """Test _set_temperature_offset with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._set_temperature_offset(temperature=1.0, zone=1)


class TestClientPrivateAntiFreezeTemperatureMethods:
    """Tests for private anti-freeze temperature methods"""

    @pytest.mark.asyncio
    async def test_get_anti_freeze_temperature_zone(self):
        """Test _get_anti_freeze_temperature for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,5"
            ]
        )

        result = await client._get_anti_freeze_temperature(zone=1)
        assert result == 5.0
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?E#1#20/")

    @pytest.mark.asyncio
    async def test_get_anti_freeze_temperature_module(self):
        """Test _get_anti_freeze_temperature for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,4"
            ]
        )

        result = await client._get_anti_freeze_temperature(zone=1, module=1)
        assert result == 4.0
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?E#1#20/")

    @pytest.mark.asyncio
    async def test_get_anti_freeze_temperature_default(self):
        """Test _get_anti_freeze_temperature for module with default value"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,255"
            ]
        )

        result = await client._get_anti_freeze_temperature(zone=1, module=1)
        assert result == 5
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?E#1#20/")

    @pytest.mark.asyncio
    async def test_get_anti_freeze_temperature_invalid_response(self):
        """Test _get_anti_freeze_temperature with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._get_anti_freeze_temperature(zone=1)

    @pytest.mark.asyncio
    async def test_set_anti_freeze_temperature_zone(self):
        """Test _set_anti_freeze_temperature for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_anti_freeze_temperature(temperature=3.5, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*SEP#1#20#3/")

    @pytest.mark.asyncio
    async def test_set_anti_freeze_temperature_module(self):
        """Test _set_anti_freeze_temperature for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )
        
        await client._set_anti_freeze_temperature(temperature=4.5, zone=1, module=1)
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*SEP#1#20#4/")

    @pytest.mark.asyncio
    async def test_set_anti_freeze_temperature_invalid_response(self):
        """Test _set_anti_freeze_temperature with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._set_anti_freeze_temperature(temperature=5.0, zone=1)


class TestClientPrivateBoostMethods:
    """Tests for private boost methods"""

    @pytest.mark.asyncio
    async def test_get_boost_zone(self):
        """Test _get_boost for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,5"
            ]
        )

        result = await client._get_boost(zone=1)
        assert isinstance(result, int)
        assert result == 25
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?E#1#22/")

    @pytest.mark.asyncio
    async def test_get_boost_module(self):
        """Test _get_boost for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,5"
            ]
        )
        
        result = await client._get_boost(zone=1, module=1)
        assert result == 25
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?E#1#22/")

    @pytest.mark.asyncio
    async def test_get_boost_module_default(self):
        """Test _get_boost for module default value"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,255"
            ]
        )

        result = await client._get_boost(zone=1, module=1)
        assert result == 0
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?E#1#22/")

    @pytest.mark.asyncio
    async def test_get_boost_invalid_response(self):
        """Test _get_boost with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._get_boost(zone=1)

    @pytest.mark.asyncio
    async def test_set_boost_zone(self):
        """Test _set_boost for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_boost(time=30, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*SEP#1#22#6/")

    @pytest.mark.asyncio
    async def test_set_boost_module(self):
        """Test _set_boost for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )
        
        await client._set_boost(time=60, zone=1, module=1)
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*SEP#1#22#12/")

    @pytest.mark.asyncio
    async def test_set_boost_too_high_failure(self):
        """Test _set_boost above limit"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidRequest):
            await client._set_boost(time=999, zone=1)

    @pytest.mark.asyncio
    async def test_set_boost_invalid_response(self):
        """Test _set_boost with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._set_boost(time=30, zone=1)


class TestClientPrivateWindowOpenDetectionMethods:
    """Tests for private window open detection methods"""

    @pytest.mark.asyncio
    async def test_is_window_open_detection_enabled_zone_true(self):
        """Test _is_window_open_detection_enabled for zone (enabled)"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,1"
            ]
        )

        result = await client._is_window_open_detection_enabled(zone=1)
        assert result is True
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?E#0#6/")

    @pytest.mark.asyncio
    async def test_is_window_open_detection_enabled_zone_false(self):
        """Test _is_window_open_detection_enabled for zone (disabled)"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,0"
            ]
        )

        result = await client._is_window_open_detection_enabled(zone=1)
        assert result is False
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?E#0#6/")

    @pytest.mark.asyncio
    async def test_is_window_open_detection_enabled_module(self):
        """Test _is_window_open_detection_enabled for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,1"
            ]
        )
        
        result = await client._is_window_open_detection_enabled(zone=1, module=1)
        assert result is True
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?E#0#6/")

    @pytest.mark.asyncio
    async def test_is_window_open_detection_enabled_invalid_response(self):
        """Test _is_window_open_detection_enabled with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._is_window_open_detection_enabled(zone=1)

    @pytest.mark.asyncio
    async def test_set_window_open_detection_zone_enable(self):
        """Test _set_window_open_detection for zone (enable)"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_window_open_detection(value=True, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*SEP#0#6#1/")

    @pytest.mark.asyncio
    async def test_set_window_open_detection_zone_disable(self):
        """Test _set_window_open_detection for zone (disable)"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_window_open_detection(value=False, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*SEP#0#6#0/")

    @pytest.mark.asyncio
    async def test_set_window_open_detection_module(self):
        """Test _set_window_open_detection for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )
        
        await client._set_window_open_detection(value=True, zone=1, module=1)
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*SEP#0#6#1/")

    @pytest.mark.asyncio
    async def test_set_window_open_detection_invalid_response(self):
        """Test _set_window_open_detection with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._set_window_open_detection(value=True, zone=1)


class TestClientPrivateSmartStartMethods:
    """Tests for private smart start methods"""

    @pytest.mark.asyncio
    async def test_is_smart_start_enabled_zone_true(self):
        """Test _is_smart_start_enabled for zone (enabled)"""
        client = Client(CLIENT_IP)
        # response = "OPOK,OPD0,,1"  # 1 = enabled
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,1"
            ]
        )

        result = await client._is_smart_start_enabled(zone=1)
        assert result is True
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?E#0#7/")

    @pytest.mark.asyncio
    async def test_is_smart_start_enabled_zone_false(self):
        """Test _is_smart_start_enabled for zone (disabled)"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,0"
            ]
        )

        result = await client._is_smart_start_enabled(zone=1)
        assert result is False
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?E#0#7/")

    @pytest.mark.asyncio
    async def test_is_smart_start_enabled_module(self):
        """Test _is_smart_start_enabled for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,1"
            ]
        )
        
        result = await client._is_smart_start_enabled(zone=1, module=1)
        assert result is True
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?E#0#7/")

    @pytest.mark.asyncio
    async def test_is_smart_start_enabled_invalid_response(self):
        """Test _is_smart_start_enabled with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._is_smart_start_enabled(zone=1)

    @pytest.mark.asyncio
    async def test_set_smart_start_zone_enable(self):
        """Test _set_smart_start for zone (enable)"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_smart_start(value=True, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*SEP#0#7#1/")

    @pytest.mark.asyncio
    async def test_set_smart_start_zone_disable(self):
        """Test _set_smart_start for zone (disable)"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._set_smart_start(value=False, zone=1)
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*SEP#0#7#0/")

    @pytest.mark.asyncio
    async def test_set_smart_start_module(self):
        """Test _set_smart_start for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )
        
        await client._set_smart_start(value=True, zone=1, module=1)
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*SEP#0#7#1/")

    @pytest.mark.asyncio
    async def test_set_smart_start_invalid_response(self):
        """Test _set_smart_start with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._set_smart_start(value=True, zone=1)


class TestClientPrivateHolidayModeMethods:
    """Tests for private holiday mode methods"""

    @pytest.mark.asyncio
    async def test_get_holiday_mode_zone(self):
        """Test _get_holiday_mode for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,RH,20,7,16,14,30,45,0,0,7,22,00,20"
            ]
        )

        result = await client._get_holiday_mode(zone=1)
        assert isinstance(result, HolidayData)
        assert result.get_current_temperature() == 20.7
        assert result.get_target_temperature() == 16.0
        assert result.get_after_holiday_temperature() == 20.0
        assert result.get_time() == "14:30:45"
        assert result.get_days_left() == 7
        assert result.get_end_time() == "22:00"
        assert result.is_holiday_mode_active() == True
        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*?RH/")

    @pytest.mark.asyncio
    async def test_get_holiday_mode_module(self):
        """Test _get_holiday_mode for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,RH,10,7,6,16,30,45,0,0,7,20,00,10"
            ]
        )
        
        result = await client._get_holiday_mode(zone=1, module=1)
        assert isinstance(result, HolidayData)
        assert result.get_current_temperature() == 10.7
        assert result.get_target_temperature() == 6.0
        assert result.get_after_holiday_temperature() == 10.0
        assert result.get_time() == "16:30:45"
        assert result.get_days_left() == 7
        assert result.get_end_time() == "20:00"
        assert result.is_holiday_mode_active() == True
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?RH/")

    @pytest.mark.asyncio
    async def test_get_holiday_mode_invalid_response(self):
        """Test _get_holiday_mode with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._get_holiday_mode(zone=1)

    @pytest.mark.asyncio
    async def test_set_holiday_mode_zone(self):
        """Test _set_holiday_mode for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        fake_now = datetime(2024, 6, 10, 12, 10, 22)
        with patch("thermotecaeroflowflexismart.client.datetime") as mock_datetime:
            mock_datetime.now.return_value = fake_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            target_date = fake_now + timedelta(days=10)

            await client._set_holiday_mode(
                target_datetime=target_date,
                temperature=16.0,
                zone=1
            )

            client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*RH#10#12#10#16/")

    @pytest.mark.asyncio
    async def test_set_holiday_mode_module(self):
        """Test _set_holiday_mode for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        fake_now = datetime(2024, 6, 10, 12, 10, 22)
        with patch("thermotecaeroflowflexismart.client.datetime") as mock_datetime:
            mock_datetime.now.return_value = fake_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            target_date = fake_now + timedelta(days=10)

            await client._set_holiday_mode(
                target_datetime=target_date,
                temperature=16.0,
                zone=1,
                module=1
            )

            client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*RH#10#12#10#16/")

    @pytest.mark.asyncio
    async def test_set_holiday_mode_too_many_days(self):
        """Test _set_holiday_mode with too many days"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        target_date = datetime.now() + timedelta(days=365)

        with pytest.raises(InvalidRequest):
            await client._set_holiday_mode(
                target_datetime=target_date,
                temperature=16.0,
                zone=1
            )

    @pytest.mark.asyncio
    async def test_set_holiday_mode_today(self):
        """Test _set_holiday_mode with date today"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        target_date = datetime.now()

        with pytest.raises(InvalidRequest):
            await client._set_holiday_mode(
                target_datetime=target_date,
                temperature=16.0,
                zone=1
            )

    @pytest.mark.asyncio
    async def test_set_holiday_mode_past(self):
        """Test _set_holiday_mode with date in past"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        target_date = datetime.now() - timedelta(days=365)

        with pytest.raises(InvalidRequest):
            await client._set_holiday_mode(
                target_datetime=target_date,
                temperature=16.0,
                zone=1
            )

    @pytest.mark.asyncio
    async def test_set_holiday_mode_invalid_response(self):
        """Test _set_holiday_mode with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        target_date = datetime.now() + timedelta(days=10)

        with pytest.raises(InvalidResponse):
            await client._set_holiday_mode(
                target_datetime=target_date,
                temperature=16.0,
                zone=1
            )

    @pytest.mark.asyncio
    async def test_disable_holiday_mode_zone(self):
        """Test _disable_holiday_mode for zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )

        await client._disable_holiday_mode(zone=1)

        client._gateway.send_message_get_response.assert_awaited_with("D#1#1#0#0*RH#0#0#0#251/")

    @pytest.mark.asyncio
    async def test_disable_holiday_mode_module(self):
        """Test _disable_holiday_mode for module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK"
            ]
        )
        
        await client._disable_holiday_mode(zone=1, module=1)
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*RH#0#0#0#251/")

    @pytest.mark.asyncio
    async def test_disable_holiday_mode_invalid_response(self):
        """Test _disable_holiday_mode with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._disable_holiday_mode(zone=1)


class TestClientPrivateRestartMethods:
    """Tests for private restart methods"""

    @pytest.mark.asyncio
    async def test_restart_module_success(self):
        """Test _restart_module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,18,8,19,2,50,59,3,0,0,0,0,1,1,129,0,4,8,9,10,v201106"
            ]
        )

        result = await client._restart_module(zone=1, module=1)
        assert isinstance(result, ModuleData)
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*-TU#0#0#0#0#2/")

    @pytest.mark.asyncio
    async def test_restart_module_invalid_response(self):
        """Test _restart_module with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._restart_module(zone=1, module=1)


class TestClientPrivateRegisterModuleMethods:
    """Tests for private module registration methods"""

    @pytest.mark.asyncio
    async def test_register_module_success(self):
        """Test _register_module"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OPOK"
            ]
        )

        await client._register_module(zone=1, timeout=30)
        client._gateway.send_message_get_response.assert_awaited_with("OPZI199,1,1/", 30)

    @pytest.mark.asyncio
    async def test_register_module_module(self):
        """Test _register_module with module number"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OPOK"
            ]
        )

        await client._register_module(zone=1, module=1, timeout=30)
        client._gateway.send_message_get_response.assert_awaited_with("OPZI199,1,1/", 30)


    @pytest.mark.asyncio
    async def test_register_module_invalid_response(self):
        """Test _register_module with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client._register_module(zone=1, timeout=30)
