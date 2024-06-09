from bleak import BleakScanner, BleakClient
from movesense_device_manager import NAME_CHARACTERISTIC

import logging
logger = logging.getLogger(__name__)


class MovesenseManager:
    def __init__(self):
        self.connected_devices = []

    def search_and_connect(self):
        print("Searching for MoveSense devices...")
        devices = BleakScanner.discover(timeout=10.0).run()
        for device in devices:
            if "Movesense" in device.name:
                print(f"Device found: {device.name} ({device.address})")
                self.connect(device)

    def connect(self, device):
        client = BleakClient(device.address)
        client.connect()
        print(f"Connected to {device.name} ({device.address})")
        self.connected_devices.append(client)

    def show_connected_devices(self):
        print("\nConnected MoveSense devices:")
        for device in self.connected_devices:
            print(f"{device.address}")

    def rename_devices(self):
        for i, device in enumerate(self.connected_devices):
            new_name = input(f"Enter a new name for device {i + 1} ({device.address}): ").strip()
            if new_name:
                device.write_gatt_char(NAME_CHARACTERISTIC, bytearray(new_name, "utf-8"), response=True)
                print(f"Device {i + 1} renamed to {new_name}")

    def disconnect_devices(self):
        print("Disconnecting from MoveSense devices...")
        for device in self.connected_devices:
            device.disconnect()
        self.connected_devices = []
