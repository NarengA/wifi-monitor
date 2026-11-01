from database.database import create_database, save_device, get_devices
from network.network_info import get_network_info
from network.devices import get_mac_addresses


def scan_and_track():
    create_database()
    info = get_network_info()

    if not info.get("local_ip") or not info.get("network"):
        print("Could not determine the active IPv4 network.")
        return

    print("\nNetwork:", info["network"])
    print("Local IP:", info["local_ip"])
    print("Gateway:", info["gateway"])
    print("\nReading the existing ARP cache...")

    devices = get_mac_addresses(info)
    if not devices:
        print(
            "No other valid unicast devices were visible in the ARP cache."
        )
        print(
            "This does NOT prove that no other devices are connected."
        )
        return

    counts = {"new": 0, "seen": 0, "ip_changed": 0}
    for ip, mac in devices.items():
        result = save_device(ip, mac)
        counts[result] += 1
        print(f"{ip:16} {mac:17} [{result}]")

    print("\nVisible devices:", len(devices))
    print("New observations:", counts["new"])
    print("Previously known:", counts["seen"])
    print("IP changes:", counts["ip_changed"])
    print("\nSaved device history:")
    for device in get_devices():
        print(
            f"{device['ip']:16} {device['mac']:17} "
            f"last seen: {device['last_seen']}"
        )

    print(
        "\nReminder: ARP visibility is incomplete. "
        "'Not seen' must not be interpreted as 'offline'."
    )
