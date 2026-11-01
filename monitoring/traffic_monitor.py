import time
import psutil

from database.database import create_database, save_traffic
from network.network_info import get_network_info


def format_bytes(value):
    units = ["B", "KB", "MB", "GB", "TB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.2f} {unit}"
        amount /= 1024


def monitor_traffic(interval=5):
    """
    Measure byte-counter changes on this computer's active interface.
    These are this PC's interface totals, not per-device router totals.
    Press Ctrl+C to stop.
    """
    create_database()
    info = get_network_info()
    interface = info.get("interface")

    if not interface:
        print("Could not identify the active network interface.")
        return

    counters = psutil.net_io_counters(pernic=True)
    if interface not in counters:
        print(f"No traffic counters found for interface: {interface}")
        return

    previous = counters[interface]
    print(f"\nMonitoring this PC's interface: {interface}")
    print(f"Sampling every {interval} second(s). Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(interval)
            current = psutil.net_io_counters(pernic=True).get(interface)

            if current is None:
                print("Interface counters are temporarily unavailable.")
                continue

            received = max(0, current.bytes_recv - previous.bytes_recv)
            sent = max(0, current.bytes_sent - previous.bytes_sent)

            save_traffic(interface, received, sent)

            print(
                f"Download: {format_bytes(received):>10} | "
                f"Upload: {format_bytes(sent):>10}"
            )
            previous = current

    except KeyboardInterrupt:
        print("\nTraffic monitoring stopped.")
