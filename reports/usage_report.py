from database.database import (
    create_database, get_traffic_summary, get_devices, get_recent_events
)


def format_bytes(value):
    units = ["B", "KB", "MB", "GB", "TB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.2f} {unit}"
        amount /= 1024


def show_report():
    create_database()
    print("\n" + "=" * 55)
    print("                 WIFI MONITOR REPORT")
    print("=" * 55)

    for period, title in [
        ("day", "Last 24 hours"),
        ("week", "Last 7 days"),
        ("month", "Last 30 days"),
    ]:
        data = get_traffic_summary(period)
        print(f"\n{title}")
        print(f"  Downloaded: {format_bytes(data['received'])}")
        print(f"  Uploaded  : {format_bytes(data['sent'])}")
        print(f"  Samples   : {data['samples']}")

    print("\nKnown devices (previously observed in ARP cache):")
    devices = get_devices()
    if not devices:
        print("  No devices recorded yet.")
    for device in devices:
        print(
            f"  {device['ip']:16} {device['mac']:17} "
            f"last seen: {device['last_seen']}"
        )

    print("\nRecent device events:")
    events = get_recent_events()
    if not events:
        print("  No events recorded yet.")
    for event in events:
        print(
            f"  {event['event_time']} | {event['event_type']} | "
            f"{event['ip']} | {event['mac']}"
        )

    print("\n" + "=" * 55)
    print(
        "Traffic totals are for this computer's interface only, "
        "not all devices on the Wi-Fi."
    )
