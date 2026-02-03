import datetime
import logging
from bleak.backends.device import BLEDevice
from .lywsd02_client import Lywsd02Client

_LOGGER = logging.getLogger(__name__)

async def sync_clock_time(ble_device: BLEDevice) -> None:
    """Sync time to a Xiaomi LYWSD02 clock."""
    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    mac = ble_device.address
    
    try:
        client = Lywsd02Client(ble_device, notification_timeout=5.0)
        async with client.connect():
            _LOGGER.debug("Connected to device %s", mac)
            await client.set_time(now)
            _LOGGER.info("Time set on device %s to %s", mac, time_str)
        _LOGGER.info("Time synced for %s at %s", mac, time_str)
    except Exception as e:
        _LOGGER.error("Failed to sync time for %s: %s (%s)", mac, e, type(e).__name__, exc_info=True)
