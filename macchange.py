#!/usr/bin/env python3

import subprocess
import re
import argparse

def validate_mac(mac):
    return re.match(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$", mac)

def get_mac(interface):
    try:
        result = subprocess.check_output(["ifconfig", interface], text=True)
        return re.search(r"([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}", result).group(0)
    except (subprocess.CalledProcessError, AttributeError):
        return None

def change_mac(interface, new_mac):
    subprocess.run(f"ifconfig {interface} down", shell=True, check=True)
    subprocess.run(f"ifconfig {interface} hw ether {new_mac}", shell=True, check=True)
    subprocess.run(f"ifconfig {interface} up", shell=True, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", required=True, help="Interface to change its MAC address")
    parser.add_argument("-m", "--mac", required=True, help="New MAC Address")
    args = parser.parse_args()

    if not validate_mac(args.mac):
        print("[-] Invalid MAC address format. Use XX:XX:XX:XX:XX:XX.")
        return

    current_mac = get_mac(args.interface)
    if not current_mac:
        print(f"[-] Could not find MAC address for interface {args.interface}.")
        return

    print(f"[+] Current MAC address: {current_mac}")
    change_mac(args.interface, args.mac)
    new_mac = get_mac(args.interface)

    if new_mac == args.mac:
        print(f"[+] MAC address successfully changed to {new_mac}.")
    else:
        print("[-] MAC address change failed.")

if __name__ == "__main__":
    main()
