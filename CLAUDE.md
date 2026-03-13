# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Home Assistant custom component that syncs time on Xiaomi LYWSD02 Bluetooth clocks via BLE. There is no build step, test suite, or local dev server — the component runs inside Home Assistant.

## Installation / Testing

Copy the folder to HA's `custom_components/xiaomi_clock_sync/` directory and add `xiaomi_clock_sync:` to `configuration.yaml`. Restart HA to reload. There is no simulator — testing requires a physical LYWSD02 device and a Bluetooth adapter.

Trigger the service from HA Developer Tools → Services → `xiaomi_clock_sync.sync_time`.

## Architecture

**Data flow:** HA service call → `__init__.py` handler → `time_sync.sync_clock_time()` → `Lywsd02Client.set_time()` → BLE GATT write

- `__init__.py` — HA entry point (`async_setup`). Registers the `sync_time` service. Passes MAC addresses directly to `bluetooth.async_ble_device_from_address`.
- `time_sync.py` — thin orchestration layer; constructs a `Lywsd02Client` and calls `set_time`.
- `lywsd02_client.py` — full BLE GATT client. Connections use an async context manager (`async with client.connect()`). Binary payloads encoded with `struct.pack/unpack`. GATT UUIDs are module-level constants.
- `services.yaml` — defines the HA service UI. The `devices` field uses a `text: multiple: true` selector for entering MAC addresses (e.g. `A4:C1:38:XX:XX:XX`).
- `manifest.json` — declares HA dependencies (`bluetooth`) and Python requirements (`bleak`, `bleak-retry-connector`).

## Key Details

**Timezone handling:** `tz_offset` in `Lywsd02Client` uses `time.localtime().tm_isdst` to detect whether DST is *currently active*. Do not change this to use `time.daylight` — that only indicates whether DST rules exist, not whether they are in effect now.

**BLE connection slots:** Adapters support 3–7 simultaneous connections. `BleakOutOfConnectionSlotsError` means slots are exhausted; restarting HA releases them.

**Adding new services:** Update both `__init__.py` (register handler) and `services.yaml` (UI schema).

**Adding new BLE operations:** Follow the pattern in `lywsd02_client.py` — define a UUID constant, use `struct` for encoding, and wrap I/O in `async with self.connect()`.

**Unexposed capabilities:** `Lywsd02Client` also supports reading battery level, sensor data (temperature/humidity), and historical records — none are currently exposed as HA services.
