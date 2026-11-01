# WiFi Monitor

A Windows-focused, Python-based home-network observation project.

## Features

- Reads local IPv4, interface, subnet, broadcast and default gateway.
- Reads entries already present in the Windows ARP cache.
- Stores devices observed over time in SQLite.
- Records first observations and IP changes.
- Measures upload/download byte-counter deltas for this computer's network interface.
- Produces basic 24-hour, 7-day and 30-day reports.

## Important limitations

1. ARP cache is not a complete client list. A device may be connected to Wi-Fi and still not appear here.
2. A device missing from ARP cache is not necessarily offline.
3. Traffic monitoring measures this computer's selected network interface only. It does not measure each other device or total router traffic.
4. This project does not attempt to bypass router isolation or access controls. Use it only on networks you own or are authorized to monitor.

## Requirements

- Windows 10/11
- Python 3.10+
- `psutil`

Install:

```bash
python -m pip install -r requirements.txt
```

## Run

Open CMD or the VS Code terminal in the project root (the folder containing `main.py`):

```bash
python main.py
```

Do not run package files by double-clicking or by executing their full file path. Run from the project root.

## Menu

1. Show network information
2. Discover currently visible ARP entries and update device history
3. Monitor this computer's network traffic (Ctrl+C stops it)
4. Show usage report
0. Exit

The SQLite database `wifi_monitor.db` is created automatically in the project root.

## Suggested test sequence

1. Run option 1 and confirm the local IP, Wi-Fi interface, subnet and gateway.
2. Run option 2. It may find no other devices; that is a valid result when ARP cache has no other local entries.
3. Run option 3 for at least 30-60 seconds while using the computer normally, then press Ctrl+C.
4. Run option 4 to view the recorded samples.

## Project layout

```text
wifi-monitor/
├── main.py
├── network/
│   ├── __init__.py
│   ├── network_info.py
│   └── devices.py
├── monitoring/
│   ├── __init__.py
│   ├── device_tracker.py
│   └── traffic_monitor.py
├── database/
│   ├── __init__.py
│   └── database.py
├── reports/
│   ├── __init__.py
│   └── usage_report.py
└── requirements.txt
```
