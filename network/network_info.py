import ipaddress
import platform
import socket
import subprocess
import re
import psutil


def _get_default_route():
    """Return (gateway, interface_ip) for the Windows default IPv4 route."""
    if platform.system() != "Windows":
        return None, None

    try:
        result = subprocess.run(
            ["route", "print", "-4"],
            capture_output=True, text=True, encoding="utf-8",
            errors="ignore", timeout=5
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, None

    # Typical route row:
    # 0.0.0.0  0.0.0.0  192.168.1.1  192.168.1.12  metric
    pattern = re.compile(
        r"^\s*0\.0\.0\.0\s+0\.0\.0\.0\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})",
        re.MULTILINE
    )
    match = pattern.search(result.stdout)
    return (match.group(1), match.group(2)) if match else (None, None)


def _get_local_ip():
    # UDP connect selects the route/interface; it does not send application data.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return None
    finally:
        sock.close()


def get_network_info():
    system = platform.system()
    gateway, route_ip = _get_default_route()
    local_ip = route_ip or _get_local_ip()

    info = {
        "os": system,
        "hostname": socket.gethostname(),
        "local_ip": local_ip,
        "interface": None,
        "netmask": None,
        "network": None,
        "broadcast": None,
        "gateway": gateway,
        "is_up": None,
    }

    if not local_ip:
        return info

    for name, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family == socket.AF_INET and address.address == local_ip:
                info["interface"] = name
                info["netmask"] = address.netmask
                info["broadcast"] = address.broadcast
                stats = psutil.net_if_stats().get(name)
                info["is_up"] = stats.isup if stats else None

                if address.netmask:
                    network = ipaddress.ip_network(
                        f"{local_ip}/{address.netmask}", strict=False
                    )
                    info["network"] = str(network)
                    # Some Windows drivers do not provide broadcast.
                    info["broadcast"] = str(network.broadcast_address)
                return info

    return info


def display_network_info():
    info = get_network_info()
    print("\n" + "=" * 55)
    print("                 NETWORK INFORMATION")
    print("=" * 55)
    for key, value in info.items():
        print(f"{key.replace('_', ' ').title():15}: {value}")
    print("=" * 55)
    return info


if __name__ == "__main__":
    display_network_info()
