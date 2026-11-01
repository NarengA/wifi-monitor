import ipaddress
import platform
import re
import subprocess


ARP_PATTERN = re.compile(
    r"(\d{1,3}(?:\.\d{1,3}){3})\s+([a-fA-F0-9-]{17})"
)


def get_mac_addresses(network_info):
    """
    Read entries already present in this Windows computer's ARP cache.
    This is passive discovery, not a complete list of Wi-Fi clients.
    """
    if platform.system() != "Windows":
        raise OSError("The current ARP parser supports Windows only.")

    network_text = network_info.get("network")
    local_ip = network_info.get("local_ip")
    gateway = network_info.get("gateway")

    if not network_text:
        return {}

    network = ipaddress.ip_network(network_text, strict=False)

    try:
        result = subprocess.run(
            ["arp", "-a"], capture_output=True, text=True,
            encoding="utf-8", errors="ignore", timeout=5
        )
    except (OSError, subprocess.TimeoutExpired):
        return {}

    devices = {}
    for ip, raw_mac in ARP_PATTERN.findall(result.stdout):
        address = ipaddress.ip_address(ip)

        if address not in network:
            continue
        if address in (network.network_address, network.broadcast_address):
            continue
        if ip in (local_ip, "0.0.0.0"):
            continue

        mac = raw_mac.upper().replace("-", ":")
        octets = [int(part, 16) for part in mac.split(":")]

        # Ignore multicast/broadcast MACs and all-zero entries.
        if octets[0] & 1 or all(part == 0 for part in octets):
            continue

        devices[ip] = mac

    return devices
