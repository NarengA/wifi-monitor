from network.network_info import get_network_info, display_network_info
from monitoring.device_tracker import scan_and_track
from monitoring.traffic_monitor import monitor_traffic
from reports.usage_report import show_report


def main():
    while True:
        print("\n" + "=" * 55)
        print("                 WIFI MONITOR")
        print("=" * 55)
        print("1. Show network information")
        print("2. Discover visible devices and update history")
        print("3. Monitor this computer's network traffic")
        print("4. Show traffic usage report")
        print("0. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            display_network_info()
        elif choice == "2":
            scan_and_track()
        elif choice == "3":
            try:
                seconds = int(input("Sampling interval in seconds [5]: ") or "5")
                monitor_traffic(max(1, seconds))
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "4":
            show_report()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
