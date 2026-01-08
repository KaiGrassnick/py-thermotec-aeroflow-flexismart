"""Unit Tests for client.py - Thermotec AeroFlow® Library

These tests use mocking to avoid actual network calls to the gateway.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from tests.const import CLIENT_IP
from thermotecaeroflowflexismart.client import Client
from thermotecaeroflowflexismart.data_object import (
    GatewayData,
    ModuleData,
    GatewayDateTime,
    Temperature, GatewayNetworkConfiguration, HolidayData, HomeAssistantModuleData,
)
from thermotecaeroflowflexismart.exception import InvalidResponse, RequestTimeout

@pytest.fixture(autouse=True)
def mock_sleep():
    with patch("thermotecaeroflowflexismart.client.sleep", new_callable=AsyncMock) as mock_sleep:
        yield mock_sleep

class TestClientInitialization:
    """Tests for Client initialization"""

    def test_client_initialization_default_port(self):
        """Test Client initialization with default port"""
        client = Client(CLIENT_IP)
        assert client._gateway._host == CLIENT_IP
        assert client._gateway._port == 6653

    def test_client_initialization_custom_port(self):
        """Test Client initialization with custom port"""
        client = Client(CLIENT_IP, 8000)
        assert client._gateway._host == CLIENT_IP
        assert client._gateway._port == 8000

    def test_client_initialization_different_hosts(self):
        """Test Client initialization with different hosts"""
        hosts = [CLIENT_IP, "10.0.0.1", "localhost"]
        for host in hosts:
            client = Client(host)
            assert client._gateway._host == host


class TestHomeAssistantIntegration:
    """Tests for Home Assistant integration methods"""

    gateway_date_time = GatewayDateTime(
        ["OPOK", "14", "30", "45", "3", "25", "12", "23", "1", "192.168.1.10", "GATEWAY001"])
    zones = [1, 2, 3]
    module_data = ModuleData(
        ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "4", "8", "9", "10",
         "v201106"])
    anti_freeze_temperature = 5.0
    holiday_data = HolidayData(["RH", "12", "9", "6", "16", "30", "45", "0", "0", "7", "20", "00", "10"])

    @pytest.mark.asyncio
    async def test_get_module_all_data(self):
        """Test get_module_all_data"""
        client = Client(CLIENT_IP)

        client.get_zones_with_module_count = AsyncMock(return_value=self.zones)
        client.get_module_data = AsyncMock(return_value=self.module_data)
        client.get_module_anti_freeze_temperature = AsyncMock(return_value=self.anti_freeze_temperature)
        client.get_module_holiday_mode = AsyncMock(return_value=self.holiday_data)
        client.get_date_time = AsyncMock(return_value=self.gateway_date_time)

        result = await client.get_module_all_data(1, 1)
        assert isinstance(result, HomeAssistantModuleData)
        assert result.get_module_id() == 1
        assert result.get_zone_id() == 1
        assert isinstance(result.get_module_data(), ModuleData)
        assert result.get_module_data() == self.module_data
        assert result.get_anti_freeze_temperature() == self.anti_freeze_temperature
        assert isinstance(result.get_holiday_data(), HolidayData)
        assert result.get_holiday_data() == self.holiday_data
        assert isinstance(result.get_date_time(), GatewayDateTime)
        assert result.get_date_time() == self.gateway_date_time

    @pytest.mark.asyncio
    async def test_get_all_data_success(self):
        """Test get_all_data"""
        client = Client(CLIENT_IP)
        client.get_zones_with_module_count = AsyncMock(return_value=self.zones)
        client.get_date_time = AsyncMock(return_value=self.gateway_date_time)
        client.get_module_data = AsyncMock(side_effect=[
            self.module_data,
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "2", "1", "1", "1",
                 "v201106"]),
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "2", "1", "1", "2",
                 "v201106"]),
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "3", "1", "1", "1",
                 "v201106"]),
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "3", "1", "1", "2",
                 "v201106"]),
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "3", "1", "1", "3",
                 "v201106"]),
        ])
        client._get_anti_freeze_temperature = AsyncMock(return_value=self.anti_freeze_temperature)
        client._get_holiday_mode = AsyncMock(return_value=self.holiday_data)

        result = await client.get_all_data()
        assert isinstance(result, dict)
        assert len(result) == 6

    @pytest.mark.asyncio
    async def test_get_all_data_empty_zone(self):
        """Test get_all_data with empty zone"""
        client = Client(CLIENT_IP)
        client.get_zones_with_module_count = AsyncMock(return_value=[1, 2, 0])
        client.get_date_time = AsyncMock(return_value=self.gateway_date_time)
        client.get_module_data = AsyncMock(side_effect=[
            self.module_data,
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "2", "1", "1", "1",
                 "v201106"]),
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "2", "1", "1", "2",
                 "v201106"])
        ])
        client._get_anti_freeze_temperature = AsyncMock(return_value=self.anti_freeze_temperature)
        client._get_holiday_mode = AsyncMock(return_value=self.holiday_data)

        result = await client.get_all_data()
        assert isinstance(result, dict)
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_all_data_invalid_device(self):
        """Test get_all_data with invalid device"""
        client = Client(CLIENT_IP)
        client.get_zones_with_module_count = AsyncMock(return_value=[1, 2, 0])
        client.get_date_time = AsyncMock(return_value=self.gateway_date_time)

        invalid_module = ModuleData(
            ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "0", "0", "0", "0",
             "v201106"])

        client.get_module_data = AsyncMock(side_effect=[
            self.module_data,
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "2", "1", "1", "1",
                 "v201106"]),
            invalid_module,
            invalid_module,
            invalid_module,
            invalid_module
        ])
        client._get_anti_freeze_temperature = AsyncMock(return_value=self.anti_freeze_temperature)
        client._get_holiday_mode = AsyncMock(return_value=self.holiday_data)

        result = await client.get_all_data()
        assert isinstance(result, dict)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_data_request_timeout(self):
        """Test get_all_data with invalid device"""
        client = Client(CLIENT_IP)
        client.get_zones_with_module_count = AsyncMock(return_value=[1, 2, 0])
        client.get_date_time = AsyncMock(return_value=self.gateway_date_time)

        client.get_module_data = AsyncMock(side_effect=[
            self.module_data,
            ModuleData(
                ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "2", "1", "1", "1",
                 "v201106"]),
            RequestTimeout(),
        ])
        client._get_anti_freeze_temperature = AsyncMock(return_value=self.anti_freeze_temperature)
        client._get_holiday_mode = AsyncMock(return_value=self.holiday_data)

        result = await client.get_all_data()
        assert isinstance(result, dict)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_data_utils_test(self):
        """Test get_all_data test utils"""
        client = Client(CLIENT_IP)

        client.get_zones_with_module_count = AsyncMock(return_value=[])

        with pytest.raises(Exception):
            await client.get_module_all_data(1, 1, [])

        with pytest.raises(Exception):
            await client.get_module_all_data(0, 1, [1, 2, 3])

        with pytest.raises(Exception):
            await client.get_module_all_data(20, 1, [1, 2, 3])

        with pytest.raises(Exception):
            await client.get_module_all_data(1, 2, [1, 2, 3])


class TestClientPing:
    """Tests for Client.ping method"""

    @pytest.mark.asyncio
    async def test_ping_success(self):
        """Test successful ping"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="OP")

        result = await client.ping()
        assert result is True
        client._gateway.send_message_get_response.assert_awaited_with("PING")

    @pytest.mark.asyncio
    async def test_ping_failure_invalid_response(self):
        """Test ping with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="INVALID")

        result = await client.ping()
        assert result is False

    @pytest.mark.asyncio
    async def test_ping_failure_timeout(self):
        """Test ping with timeout"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(side_effect=RequestTimeout())

        result = await client.ping()
        assert result is False


class TestClientDateTime:
    """Tests for Client date/time methods"""

    @pytest.mark.asyncio
    async def test_get_date_time_success(self):
        """Test successful get_date_time"""
        client = Client(CLIENT_IP)
        response = "OPOK,14,30,45,3,25,12,23,1,192.168.1.100,GATEWAY001"
        client._gateway.send_message_get_response = AsyncMock(return_value=response)

        result = await client.get_date_time()
        assert isinstance(result, GatewayDateTime)
        assert result.get_date_time_string() == "25.12.2023 14:30:45"
        assert result.get_time() == "14:30:45"
        assert result.get_date() == "25.12.2023"
        assert result.get_ip() == "192.168.1.100"
        assert result.get_id() == "GATEWAY001"
        client._gateway.send_message_get_response.assert_awaited_with("OPH/")

    @pytest.mark.asyncio
    async def test_get_date_time_invalid_response(self):
        """Test get_date_time with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="INVALID")

        with pytest.raises(InvalidResponse):
            await client.get_date_time()

    @pytest.mark.asyncio
    async def test_set_date_time_success(self):
        """Test successful set_date_time"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="OPOK")

        target_time = datetime(2023, 12, 25, 14, 30, 45)
        await client.set_date_time(target_time)
        client._gateway.send_message_get_response.assert_awaited_with("OPF1430450/25,12,23/")

    @pytest.mark.asyncio
    async def test_set_date_time_invalid_response(self):
        """Test set_date_time with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="INVALID")

        target_time = datetime(2023, 12, 25, 14, 30, 45)
        with pytest.raises(InvalidResponse):
            await client.set_date_time(target_time)

    @pytest.mark.asyncio
    async def test_update_date_time(self):
        """Test update_date_time calls set_date_time"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="OPOK")

        fake_now = datetime(2024, 6, 10, 12, 10, 22)
        with patch("thermotecaeroflowflexismart.client.datetime") as mock_datetime:
            mock_datetime.now.return_value = fake_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            await client.update_date_time()

        client._gateway.send_message_get_response.assert_awaited_with("OPF1210220/10,06,24/")


class TestClientGatewayData:
    """Tests for Client gateway data methods"""

    @pytest.mark.asyncio
    async def test_get_gateway_data_success(self):
        """Test successful get_gateway_data"""
        client = Client(CLIENT_IP)
        response = "OPOK,1.2.3,12345,IDU123"
        client._gateway.send_message_get_response = AsyncMock(return_value=response)

        result = await client.get_gateway_data()
        assert isinstance(result, GatewayData)
        assert result.get_firmware() == "1.2.3"
        assert result.get_installation_id() == "12345"
        assert result.get_idu() == "IDU123"
        client._gateway.send_message_get_response.assert_awaited_with("OPF/")

    @pytest.mark.asyncio
    async def test_get_gateway_data_invalid_response(self):
        """Test get_gateway_data with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="INVALID")

        with pytest.raises(InvalidResponse):
            await client.get_gateway_data()


class TestClientStatus:
    """Tests for Client status methods"""

    @pytest.mark.asyncio
    async def test_get_status_success(self):
        """Test successful get_status"""
        client = Client(CLIENT_IP)
        response = "OPOK,OPS1,123,122,0,0,0,16,197,215,34,0"
        client._gateway.send_message_get_response = AsyncMock(return_value=response)

        result = await client.get_status()
        assert isinstance(result, dict)
        assert result["serverSyncId"] == "123"
        assert result["idA"] == "16"
        assert result["idB"] == "197"
        client._gateway.send_message_get_response.assert_awaited_with("OPS1/")

    @pytest.mark.asyncio
    async def test_get_status_invalid_response(self):
        """Test get_status with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="INVALID")

        with pytest.raises(InvalidResponse):
            await client.get_status()


class TestClientZones:
    """Tests for Client zone methods"""

    @pytest.mark.asyncio
    async def test_create_zone_success(self):
        """Test successful create_zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OPOK"
            ]
        )

        await client.create_zone()
        client._gateway.send_message_get_response.assert_awaited_with("OPMW12,4/")

    @pytest.mark.asyncio
    async def test_create_zone_invalid_response(self):
        """Test create_zone with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client.create_zone()

    @pytest.mark.asyncio
    async def test_delete_zone_success(self):
        """Test successful delete_zone"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OPOK"
            ]
        )

        await client.delete_zone(1)
        client._gateway.send_message_get_response.assert_awaited_with("OPMW129,0/")

    @pytest.mark.asyncio
    async def test_delete_zone_invalid_response(self):
        """Test delete_zone with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client.delete_zone(1)

    @pytest.mark.asyncio
    async def test_get_zones_success(self):
        """Test successful get_zones"""
        client = Client(CLIENT_IP)
        response = "OPOK,OPS2,1,2,3,4"
        client._gateway.send_message_get_response = AsyncMock(return_value=response)

        result = await client.get_zones()
        assert isinstance(result, list)
        assert result == [1, 2, 3, 4]
        client._gateway.send_message_get_response.assert_awaited_with("OPS2/")

    @pytest.mark.asyncio
    async def test_get_zones_invalid_response(self):
        """Test get_zones with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="INVALID")

        with pytest.raises(InvalidResponse):
            await client.get_zones()

    @pytest.mark.asyncio
    async def test_get_zones_with_module_count_success(self):
        """Test successful get_zones_with_module_count"""
        client = Client(CLIENT_IP)
        response = "OPOK,OPS3,1,1,0,3"
        client._gateway.send_message_get_response = AsyncMock(return_value=response)

        result = await client.get_zones_with_module_count()
        assert isinstance(result, list)
        assert result == [1, 1, 0, 3]
        client._gateway.send_message_get_response.assert_awaited_with("OPS3/")

    @pytest.mark.asyncio
    async def test_get_zones_with_module_count_invalid_response(self):
        """Test get_zones_with_module_count with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="INVALID")

        with pytest.raises(InvalidResponse):
            await client.get_zones_with_module_count()

    @pytest.mark.asyncio
    async def test_restart_zone(self):
        """Test restart_zone"""
        client = Client(CLIENT_IP)
        client._restart_module = AsyncMock(return_value=ModuleData(
            ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "4", "8", "9", "10",
             "v201106"]))

        result = await client.restart_zone(1)
        assert isinstance(result, ModuleData)
        client._restart_module.assert_called_once()

    @pytest.mark.asyncio
    async def test_restart_module(self):
        """Test restart_module"""
        client = Client(CLIENT_IP)
        client._restart_module = AsyncMock(return_value=ModuleData(
            ["18", "8", "19", "2", "50", "59", "3", "0", "0", "0", "0", "1", "1", "129", "0", "4", "8", "9", "10",
             "v201106"]))

        result = await client.restart_module(zone=1, module=1, zones=None)
        assert isinstance(result, ModuleData)
        client._restart_module.assert_called_once()


class TestClientModuleData:
    """Tests for Client module data methods"""

    @pytest.mark.asyncio
    async def test_get_module_data_success(self):
        """Test successful get_module_data"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,18,8,19,2,50,59,3,0,0,0,0,1,1,129,0,4,8,9,10,v201106"
            ]
        )

        result = await client.get_module_data(1, 1)
        assert isinstance(result, ModuleData)
        assert result.get_current_temperature() == 18.8
        assert result.get_target_temperature() == 19.0
        assert result.get_time() == "02:50:59"
        assert result.get_programming_string() == "0,0"
        assert result.get_boost_time_left() == 0
        assert result.get_boost_time_left_string() == "< 0 min."
        assert result.is_boost_active() == False
        assert result.get_temperature_offset() == 0.0
        assert result.is_smart_start_enabled() == True
        assert result.is_window_open_detection_enabled() == True
        assert result.get_language() == "English"
        assert result.get_device_identifier() == "4.8.9.10"
        assert result.get_firmware_version() == "v201106"
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?F/")

    @pytest.mark.asyncio
    async def test_get_module_data_german(self):
        """Test successful get_module_data with language german"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,18,8,19,2,50,59,3,0,0,0,0,1,1,128,0,4,8,9,10,v201106"
            ]
        )

        result = await client.get_module_data(1, 1)
        assert isinstance(result, ModuleData)
        assert result.get_current_temperature() == 18.8
        assert result.get_target_temperature() == 19.0
        assert result.get_time() == "02:50:59"
        assert result.get_programming_string() == "0,0"
        assert result.get_boost_time_left() == 0
        assert result.get_boost_time_left_string() == "< 0 min."
        assert result.is_boost_active() == False
        assert result.get_temperature_offset() == 0.0
        assert result.is_smart_start_enabled() == True
        assert result.is_window_open_detection_enabled() == True
        assert result.get_language() == "Deutsch"
        assert result.get_device_identifier() == "4.8.9.10"
        assert result.get_firmware_version() == "v201106"
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?F/")

    @pytest.mark.asyncio
    async def test_get_module_data_boost_time(self):
        """Test successful get_module_data with boost time"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "OK,18,8,19,2,50,59,3,0,0,20,0,1,1,128,0,4,8,9,10,v201106"
            ]
        )

        result = await client.get_module_data(1, 1)
        assert isinstance(result, ModuleData)
        assert result.get_current_temperature() == 18.8
        assert result.get_target_temperature() == 19.0
        assert result.get_time() == "02:50:59"
        assert result.get_programming_string() == "0,0"
        assert result.get_boost_time_left() == 10
        assert result.get_boost_time_left_string() == "< 10 min."
        assert result.is_boost_active() == True
        assert result.get_temperature_offset() == 0.0
        assert result.is_smart_start_enabled() == True
        assert result.is_window_open_detection_enabled() == True
        assert result.get_language() == "Deutsch"
        assert result.get_device_identifier() == "4.8.9.10"
        assert result.get_firmware_version() == "v201106"
        client._gateway.send_message_get_response.assert_awaited_with("R#1#1#0#0*?F/")

    @pytest.mark.asyncio
    async def test_get_module_data_invalid_response(self):
        """Test get_module_data with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(
            side_effect=[
                "OPOK,OPS3,1,2,3",
                "INVALID"
            ]
        )

        with pytest.raises(InvalidResponse):
            await client.get_module_data(1, 1)


class TestClientNetworkConfiguration:
    """Tests for Client network configuration methods"""

    @pytest.mark.asyncio
    async def test_get_network_configuration_success(self):
        """Test successful get_network_configuration"""
        client = Client(CLIENT_IP)
        response = "OPOK,OPS38,10,255,255,20,10,0,0,1,255,0,0,0,48,48,48,52,97,51,48,48,49,53,49,53,66,53,1,1,51,254,215,41,66,51"
        client._gateway.send_message_get_response = AsyncMock(return_value=response)

        result = await client.get_network_configuration()
        assert isinstance(result, GatewayNetworkConfiguration)
        assert result.get_ip() == "10.255.255.20"
        assert result.get_port() == 6653
        assert result.get_ip_with_port() == "10.255.255.20:6653"
        assert result.get_gateway() == "10.0.0.1"
        assert result.get_subnet_mask() == "255.0.0.0"
        assert result.get_registration_server_ip() == "51.254.215.41"
        assert result.get_registration_server_port() == 6651
        assert result.get_registration_server_ip_with_port() == "51.254.215.41:6651"
        client._gateway.send_message_get_response.assert_awaited_with("OPS38/")

    @pytest.mark.asyncio
    async def test_get_network_configuration_invalid_response(self):
        """Test get_network_configuration with invalid response"""
        client = Client(CLIENT_IP)
        client._gateway.send_message_get_response = AsyncMock(return_value="INVALID")

        with pytest.raises(InvalidResponse):
            await client.get_network_configuration()


class TestClientRegisterInZone:
    """Tests for Client register in zone methods"""

    @pytest.mark.asyncio
    async def test_register_module_in_zone_success(self):
        """Test successful register_module_in_zone"""
        client = Client(CLIENT_IP)
        client._register_module = AsyncMock(return_value=None)

        await client.register_module_in_zone(1)
        client._register_module.assert_called_once()


class TestClientTemperatureMethods:
    """Tests for Client temperature methods"""

    @pytest.mark.asyncio
    async def test_get_zone_temperature_success(self):
        """Test successful get_zone_temperature"""
        client = Client(CLIENT_IP)
        response = "OPOK,OPT0,,20,5,22"
        client._gateway.send_message_get_response = AsyncMock(return_value=response)
        client._get_temperature = AsyncMock(return_value=Temperature(["20", "5", "22"]))

        result = await client.get_zone_temperature(1)
        assert isinstance(result, Temperature)
        assert result.get_current_temperature() == 20.5
        assert result.get_target_temperature() == 22

    @pytest.mark.asyncio
    async def test_set_zone_temperature_success(self):
        """Test successful set_zone_temperature"""
        client = Client(CLIENT_IP)
        client._set_temperature = AsyncMock(return_value=None)

        await client.set_zone_temperature(1, 22.5)
        client._set_temperature.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_module_temperature_success(self):
        """Test successful get_module_temperature"""
        client = Client(CLIENT_IP)
        client._set_temperature = AsyncMock(return_value=None)
        client._get_temperature = AsyncMock(return_value=Temperature(["20", "5", "22"]))

        result = await client.get_module_temperature(1, 1)
        assert isinstance(result, Temperature)
        assert result.get_current_temperature() == 20.5
        assert result.get_target_temperature() == 22

    @pytest.mark.asyncio
    async def test_set_module_temperature_success(self):
        """Test successful set_module_temperature"""
        client = Client(CLIENT_IP)
        client._set_temperature = AsyncMock(return_value=None)

        await client.set_module_temperature(1, 1, 21.0)
        client._set_temperature.assert_called_once()


class TestClientWindowOpenDetection:
    """Tests for Client window open detection methods"""

    @pytest.mark.asyncio
    async def test_is_zone_window_open_detection_enabled(self):
        """Test is_zone_window_open_detection_enabled"""
        client = Client(CLIENT_IP)
        client._is_window_open_detection_enabled = AsyncMock(return_value=True)

        result = await client.is_zone_window_open_detection_enabled(1)
        assert result is True

    @pytest.mark.asyncio
    async def test_enable_zone_window_open_detection(self):
        """Test enable_zone_window_open_detection"""
        client = Client(CLIENT_IP)
        client._set_window_open_detection = AsyncMock(return_value=None)

        await client.enable_zone_window_open_detection(1)
        client._set_window_open_detection.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_zone_window_open_detection(self):
        """Test disable_zone_window_open_detection"""
        client = Client(CLIENT_IP)
        client._set_window_open_detection = AsyncMock(return_value=None)

        await client.disable_zone_window_open_detection(1)
        client._set_window_open_detection.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_zone_window_open_detection(self):
        """Test set_zone_window_open_detection"""
        client = Client(CLIENT_IP)
        client._set_window_open_detection = AsyncMock(return_value=None)

        await client.set_zone_window_open_detection(1, True)
        client._set_window_open_detection.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_module_window_open_detection_enabled(self):
        """Test is_module_window_open_detection_enabled"""
        client = Client(CLIENT_IP)
        client._is_window_open_detection_enabled = AsyncMock(return_value=True)

        result = await client.is_module_window_open_detection_enabled(1, 1)
        assert result is True

    @pytest.mark.asyncio
    async def test_enable_module_window_open_detection(self):
        """Test enable_module_window_open_detection"""
        client = Client(CLIENT_IP)
        client._set_window_open_detection = AsyncMock(return_value=None)

        await client.enable_module_window_open_detection(1, 1)
        client._set_window_open_detection.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_module_window_open_detection(self):
        """Test disable_module_window_open_detection"""
        client = Client(CLIENT_IP)
        client._set_window_open_detection = AsyncMock(return_value=None)

        await client.disable_module_window_open_detection(1, 1)
        client._set_window_open_detection.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_module_window_open_detection(self):
        """Test set_module_window_open_detection"""
        client = Client(CLIENT_IP)
        client._set_window_open_detection = AsyncMock(return_value=None)

        await client.set_module_window_open_detection(1, 1, True)
        client._set_window_open_detection.assert_called_once()


class TestClientSmartStart:
    """Tests for Client smart start methods"""

    @pytest.mark.asyncio
    async def test_is_zone_smart_start_enabled(self):
        """Test is_zone_smart_start_enabled"""
        client = Client(CLIENT_IP)
        client._is_smart_start_enabled = AsyncMock(return_value=True)

        result = await client.is_zone_smart_start_enabled(1)
        assert result is True

    @pytest.mark.asyncio
    async def test_enable_zone_smart_start(self):
        """Test enable_zone_smart_start"""
        client = Client(CLIENT_IP)
        client._set_smart_start = AsyncMock(return_value=None)

        await client.enable_zone_smart_start(1)
        client._set_smart_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_zone_smart_start(self):
        """Test disable_zone_smart_start"""
        client = Client(CLIENT_IP)
        client._set_smart_start = AsyncMock(return_value=None)

        await client.disable_zone_smart_start(1)
        client._set_smart_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_zone_smart_start(self):
        """Test set_zone_smart_start"""
        client = Client(CLIENT_IP)
        client._set_smart_start = AsyncMock(return_value=None)

        await client.set_zone_smart_start(1, True)
        client._set_smart_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_module_smart_start_enabled(self):
        """Test is_module_smart_start_enabled"""
        client = Client(CLIENT_IP)
        client._is_smart_start_enabled = AsyncMock(return_value=True)

        result = await client.is_module_smart_start_enabled(1, 1)
        assert result is True

    @pytest.mark.asyncio
    async def test_enable_module_smart_start(self):
        """Test enable_module_smart_start"""
        client = Client(CLIENT_IP)
        client._set_smart_start = AsyncMock(return_value=None)

        await client.enable_module_smart_start(1, 1)
        client._set_smart_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_module_smart_start(self):
        """Test disable_module_smart_start"""
        client = Client(CLIENT_IP)
        client._set_smart_start = AsyncMock(return_value=None)

        await client.disable_module_smart_start(1, 1)
        client._set_smart_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_module_smart_start(self):
        """Test set_module_smart_start"""
        client = Client(CLIENT_IP)
        client._set_smart_start = AsyncMock(return_value=None)

        await client.set_module_smart_start(1, 1, True)
        client._set_smart_start.assert_called_once()


class TestClientHolidayMethods:
    """Tests for Client holiday methods"""

    @pytest.mark.asyncio
    async def test_get_zone_holiday_mode(self):
        """Test get_zone_holiday_mode"""
        client = Client(CLIENT_IP)
        client._get_holiday_mode = AsyncMock(
            return_value=HolidayData(["RH", "12", "9", "6", "16", "30", "45", "0", "0", "7", "20", "00", "10"]))

        result = await client.get_zone_holiday_mode(1)
        assert isinstance(result, HolidayData)
        assert result.get_current_temperature() == 12.9
        assert result.get_target_temperature() == 6.0
        assert result.get_after_holiday_temperature() == 10.0
        assert result.get_time() == "16:30:45"
        assert result.get_days_left() == 7
        assert result.get_end_time() == "20:00"
        assert result.is_holiday_mode_active() == True

    @pytest.mark.asyncio
    async def test_disable_zone_holiday_mode(self):
        """Test disable_zone_holiday_mode"""
        client = Client(CLIENT_IP)
        client._disable_holiday_mode = AsyncMock(return_value=None)

        await client.disable_zone_holiday_mode(1)
        client._disable_holiday_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_zone_holiday_mode(self):
        """Test set_zone_holiday_mode"""
        client = Client(CLIENT_IP)
        client._set_holiday_mode = AsyncMock(return_value=None)

        target_date = datetime.now() + timedelta(days=10)

        await client.set_zone_holiday_mode(1, target_date, 10.0)
        client._set_holiday_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_module_holiday_mode(self):
        """Test get_module_holiday_mode"""
        client = Client(CLIENT_IP)
        client._get_holiday_mode = AsyncMock(
            return_value=HolidayData(["RH", "14", "12", "6", "16", "30", "45", "0", "0", "7", "20", "00", "10"]))

        result = await client.get_module_holiday_mode(1, 1)
        assert isinstance(result, HolidayData)
        assert result.get_current_temperature() == 14.12
        assert result.get_target_temperature() == 6.0
        assert result.get_after_holiday_temperature() == 10.0
        assert result.get_time() == "16:30:45"
        assert result.get_days_left() == 7
        assert result.get_end_time() == "20:00"
        assert result.is_holiday_mode_active() == True

    @pytest.mark.asyncio
    async def test_get_module_holiday_mode_default_days(self):
        """Test get_module_holiday_mode"""
        client = Client(CLIENT_IP)
        client._get_holiday_mode = AsyncMock(
            return_value=HolidayData(["RH", "14", "12", "6", "16", "30", "45", "0", "0", "250", "20", "00", "10"]))

        result = await client.get_module_holiday_mode(1, 1)
        assert isinstance(result, HolidayData)
        assert result.get_current_temperature() == 14.12
        assert result.get_target_temperature() == 6.0
        assert result.get_after_holiday_temperature() == 10.0
        assert result.get_time() == "16:30:45"
        assert result.get_days_left() == 0
        assert result.get_end_time() == "20:00"
        assert result.is_holiday_mode_active() == False

    @pytest.mark.asyncio
    async def test_disable_module_holiday_mode(self):
        """Test disable_module_holiday_mode"""
        client = Client(CLIENT_IP)
        client._disable_holiday_mode = AsyncMock(return_value=None)

        await client.disable_module_holiday_mode(1, 1)
        client._disable_holiday_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_module_holiday_mode(self):
        """Test set_module_holiday_mode"""
        client = Client(CLIENT_IP)
        client._set_holiday_mode = AsyncMock(return_value=None)

        target_date = datetime.now() + timedelta(days=10)

        await client.set_module_holiday_mode(1, 1, target_date, 10.0)
        client._set_holiday_mode.assert_called_once()


class TestClientBoost:
    """Tests for Client boost methods"""

    @pytest.mark.asyncio
    async def test_get_zone_boost(self):
        """Test get_zone_boost"""
        client = Client(CLIENT_IP)
        client._get_boost = AsyncMock(return_value=10)

        result = await client.get_zone_boost(1)
        assert result == 10

    @pytest.mark.asyncio
    async def test_set_zone_boost(self):
        """Test set_zone_boost"""
        client = Client(CLIENT_IP)
        client._set_boost = AsyncMock(return_value=None)

        await client.set_zone_boost(1, 15)
        client._set_boost.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_module_boost(self):
        """Test get_module_boost"""
        client = Client(CLIENT_IP)
        client._get_boost = AsyncMock(return_value=10)

        result = await client.get_module_boost(1, 1)
        assert result == 10

    @pytest.mark.asyncio
    async def test_set_module_boost(self):
        """Test set_module_boost"""
        client = Client(CLIENT_IP)
        client._set_boost = AsyncMock(return_value=None)

        await client.set_module_boost(1, 1, 15)
        client._set_boost.assert_called_once()


class TestClientTemperatureOffset:
    """Tests for Client temperature offset methods"""

    @pytest.mark.asyncio
    async def test_get_zone_temperature_offset(self):
        """Test get_zone_temperature_offset"""
        client = Client(CLIENT_IP)
        client._get_temperature_offset = AsyncMock(return_value=1.5)

        result = await client.get_zone_temperature_offset(1)
        assert result == 1.5

    @pytest.mark.asyncio
    async def test_set_zone_temperature_offset(self):
        """Test set_zone_temperature_offset"""
        client = Client(CLIENT_IP)
        client._set_temperature_offset = AsyncMock(return_value=None)

        await client.set_zone_temperature_offset(1, 2.0)
        client._set_temperature_offset.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_module_temperature_offset(self):
        """Test get_module_temperature_offset"""
        client = Client(CLIENT_IP)
        client._get_temperature_offset = AsyncMock(return_value=-1.0)

        result = await client.get_module_temperature_offset(1, 1)
        assert result == -1.0

    @pytest.mark.asyncio
    async def test_set_module_temperature_offset(self):
        """Test set_module_temperature_offset"""
        client = Client(CLIENT_IP)
        client._set_temperature_offset = AsyncMock(return_value=None)

        await client.set_module_temperature_offset(1, 1, 0.5)
        client._set_temperature_offset.assert_called_once()


class TestClientAntiFreezeTemperature:
    """Tests for Client anti-freeze temperature methods"""

    @pytest.mark.asyncio
    async def test_get_zone_anti_freeze_temperature(self):
        """Test get_zone_anti_freeze_temperature"""
        client = Client(CLIENT_IP)
        client._get_anti_freeze_temperature = AsyncMock(return_value=5.0)

        result = await client.get_zone_anti_freeze_temperature(1)
        assert result == 5.0

    @pytest.mark.asyncio
    async def test_set_zone_anti_freeze_temperature(self):
        """Test set_zone_anti_freeze_temperature"""
        client = Client(CLIENT_IP)
        client._set_anti_freeze_temperature = AsyncMock(return_value=None)

        await client.set_zone_anti_freeze_temperature(1, 4.0)
        client._set_anti_freeze_temperature.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_module_anti_freeze_temperature(self):
        """Test get_module_anti_freeze_temperature"""
        client = Client(CLIENT_IP)
        client._get_anti_freeze_temperature = AsyncMock(return_value=3.0)

        result = await client.get_module_anti_freeze_temperature(1, 1)
        assert result == 3.0

    @pytest.mark.asyncio
    async def test_set_module_anti_freeze_temperature(self):
        """Test set_module_anti_freeze_temperature"""
        client = Client(CLIENT_IP)
        client._set_anti_freeze_temperature = AsyncMock(return_value=None)

        await client.set_module_anti_freeze_temperature(1, 1, 4.5)
        client._set_anti_freeze_temperature.assert_called_once()
