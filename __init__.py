import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.components import bluetooth
from .time_sync import sync_clock_time

_LOGGER = logging.getLogger(__name__)
DOMAIN = "xiaomi_clock_sync"

async def async_setup(hass: HomeAssistant, config: dict):
    async def handle_sync_time(call: ServiceCall):
        device_ids = call.data.get("devices", [])

        if not device_ids:
            _LOGGER.error("No devices specified for time sync")
            return

        for device_id in device_ids:
            # Get the BLEDevice from HA's bluetooth integration
            ble_device = bluetooth.async_ble_device_from_address(
                hass, device_id, connectable=True
            )
            
            if ble_device is None:
                _LOGGER.error(
                    "Device %s not found or not connectable. "
                    "Make sure the device is in range and discovered by Home Assistant.",
                    device_id
                )
                continue
            
            _LOGGER.debug("Found BLE device: %s (%s)", ble_device.name, ble_device.address)
            await sync_clock_time(ble_device)

    hass.services.async_register(DOMAIN, "sync_time", handle_sync_time)
    return True
