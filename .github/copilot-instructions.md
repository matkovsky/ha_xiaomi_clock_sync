# Copilot Instructions for Xiaomi Clock Time Sync

## Project Overview

Home Assistant custom component that synchronizes time on Xiaomi LYWSD02 Bluetooth thermometer/hygrometer clocks. Uses BLE (Bluetooth Low Energy) via the `bleak` library.

## Architecture

```
__init__.py          → HA integration entry point, registers services
time_sync.py         → Orchestrates time sync, wraps BLE client
lywsd02_client.py    → BLE protocol implementation (GATT characteristics)
services.yaml        → HA service UI definition
manifest.json        → HA component metadata & dependencies
```

**Data flow:** HA service call → `__init__.py` → `time_sync.sync_clock_time()` → `Lywsd02Client.set_time()` → BLE GATT write

## Key Patterns

### Home Assistant Integration Pattern
- Use `async_setup()` for component initialization (not `setup()`)
- Register services via `hass.services.async_register(DOMAIN, service_name, handler)`
- All I/O operations must be `async` - HA runs on asyncio event loop

### BLE Client Pattern (lywsd02_client.py)
- Uses async context manager for connection lifecycle: `async with client.connect():`
- GATT UUIDs are constants at module level (e.g., `UUID_TIME`, `UUID_DATA`)
- Data encoding uses `struct.pack/unpack` for binary BLE payloads
- Time format: 4-byte timestamp + 1-byte timezone offset (`'Ib'` format)

### Timezone Handling
- The `tz_offset` property calculates the current timezone offset in hours
- Uses `time.localtime().tm_isdst` to check if DST is **currently active** (not just defined)
- Important: `time.daylight` only indicates if DST rules exist for the timezone, not if DST is active now
- `time.altzone` = DST offset, `time.timezone` = standard time offset

### Error Handling
- Wrap BLE operations in try/except - connections can fail
- Log errors via `_LOGGER.error()`, use `_LOGGER.debug()` for verbose info

## Important Constants

```python
# BLE GATT Characteristic UUIDs (lywsd02_client.py)
UUID_TIME = 'EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6'  # Read/write time
UUID_DATA = 'EBE0CCC1-7A0A-4B0C-8A1A-6FF2997DA3A6'  # Sensor readings
UUID_BATTERY = 'EBE0CCC4-7A0A-4B0C-8A1A-6FF2997DA3A6'
```

## Development Notes

- **Dependencies:** Only `bleak` - auto-installed by HA from `manifest.json`
- **Testing:** Requires actual LYWSD02 device + Bluetooth adapter (no simulator)
- **MAC format:** Standard colon-separated (e.g., `A4:C1:38:XX:XX:XX`)
- **Logging:** Component uses `xiaomi_clock_sync` logger namespace

## Common Issues

- **BLE connection slots:** Adapters have limited slots (3-7). `BleakOutOfConnectionSlotsError` means slots are exhausted - restart HA or wait for timeouts
- **Time off by 1 hour:** Was caused by using `time.daylight` instead of `time.localtime().tm_isdst` for DST detection. Fixed in `tz_offset` property

## When Modifying

- Adding new BLE operations: Follow `lywsd02_client.py` pattern with UUID constants and `struct` encoding
- Adding new services: Update both `__init__.py` (handler) and `services.yaml` (UI schema)
- The `Lywsd02Client` has additional capabilities (battery, sensor data, history) not exposed via HA services yet
