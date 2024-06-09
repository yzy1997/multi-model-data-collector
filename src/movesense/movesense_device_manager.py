import asyncio
import struct
import os
import pandas as pd
import numpy as np
import gc
import weakref
import importlib

import logging

logger = logging.getLogger("__main__")

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

from src.movesense.movesense_sensor import MovesenseSensor

WRITE_CHARACTERISTIC = "34800001-7185-4d5d-b431-630e7050e8f0"
NOTIFY_CHARACTERISTIC = "34800002-7185-4d5d-b431-630e7050e8f0"
NAME_CHARACTERISTIC = ""


class ConnectedDevice:
    def __init__(self, device: BLEDevice, client: BleakClient):
        self.device = device
        self.client = client
        self.sensors = {}
        self.data_back = None

    # Distribution to individual sensor handlers
    async def notification_handler(self, sender, data):
        # Read just the start of the data for id purposes
        id_data = data[:2]

        n = len(data)

        # little endian, start char, id char, uint32 timestamp, self.unify_notifications()samples...
        packet_structure = '<' + 2 * 'c'
        packet = struct.unpack(packet_structure, id_data)
        sensor_id = int.from_bytes(packet[1], byteorder='little')

        await self.sensors[sensor_id].notification_handler(self.device.address, data)


class MovesenseDeviceManager:
    def __init__(self, config=None):
        self.loop = asyncio.get_event_loop()  # Create an event loop
        self.connected_devices = []

        # If we have a predefined session config, we utilize it
        if config:
            self.config = config

            for d in config["devices"]:

                connected_device = self.search_and_connect(d['address'])

                for path in d['paths']:
                    self.subsribe_to_sensor(connected_device, path)

            logger.info("Session config loaded.")

            self.output_file = config["output"]["filename"]
            self.output_path = config["output"]["path"]
        else:
            logger.info("No session config found.")
            self.output_file = "data_collection.csv"
            self.output_path = "./"

        os.makedirs(self.output_path, exist_ok=True)


    def run_coroutine_sync(self, coroutine):
        return self.loop.run_until_complete(coroutine)

    def get_available_devices(self, show_all=False, logging=False):
        logger.info("Searching for available devices...")
        devices = self.run_coroutine_sync(BleakScanner.discover(timeout=5.0))
        found_devices = []
        for device in devices:
            if show_all or "movesense" in device.name.lower():
                found_devices.append(device)
                if logging:
                    logger.info(f"Found device: {len(found_devices)}. {device.name} - {device.address}")

        return found_devices

    def connect(self, device):
        return self.run_coroutine_sync(self._async_connect(device))
# a bug may be present in the connect method, running time connection error
    # *****************************************************
    async def _async_connect(self, device):
        client = BleakClient(device.address)
        await client.connect()
        logger.info(f"Connected to {device.name} ({device.address})")
        connected_device = ConnectedDevice(device, client)
        self.connected_devices.append(connected_device)
        return connected_device

    def search_and_connect(self, address):

        async def connection_coroutine(available_devices, address):
            connectable_device = next((device for device in available_devices if device.address == address), None)

            if connectable_device is None:
                logger.error(f"Could not connect to device {address}")

            return await self._async_connect(connectable_device)

        # Separated so async contexts don't start new async contexts.
        available_devices = self.get_available_devices(logging=False)
        return self.run_coroutine_sync(connection_coroutine(available_devices, address))

    def show_connected_devices(self):
        logger.info("Connected MoveSense devices:")
        for i, device in enumerate(self.connected_devices):
            logger.info(f"{i + 1}. {device.device.name}: {device.device.address}")

    def rename_device(self, device, new_name):
        async def rename_coroutine(device, new_name):
            await device.client.write_gatt_char(NAME_CHARACTERISTIC, new_name, response=True)

        self.run_coroutine_sync(rename_coroutine(device, new_name))

    def subsribe_to_sensor(self, device, sensor):
        async def subsribe_coroutine(device, sensor):
            # Allow path creation of the sensor.
            if isinstance(sensor, str):
                sensor = MovesenseSensor.from_path(sensor)

            await device.client.write_gatt_char(WRITE_CHARACTERISTIC, sensor.path, response=True)
            device.sensors[sensor.id] = sensor

        self.run_coroutine_sync(subsribe_coroutine(device, sensor))

    def start_data_collection_sync(self):
        logger.debug("Enabling notifications.")
        # Subscribe to notify for all connected devices
        for device in self.connected_devices:
            self.loop.run_until_complete(self.start_notify_coroutine(device))
        
        logger.debug("Data collection started.")
    
    # this start_data_collection_sync_1 method is for streaming data
    def start_data_collection_sync_1(self):
        logger.debug("Enabling notifications.")
        # Subscribe to notify for all connected devices
        for device in self.connected_devices:
            self.loop.run_until_complete(self.start_notify_coroutine(device))
        # data_frame = self.unify_notifications()
        logger.debug("Data collection started.")
        # return data_frame

    async def start_notify_coroutine(self, device):
        await device.client.start_notify(NOTIFY_CHARACTERISTIC, lambda sender, data: asyncio.ensure_future(
            device.notification_handler(sender, data)))
# ****************************************************************************
    def end_data_collection(self):
        logger.debug("Disabling notifications.")

        for device in self.connected_devices:
            self.run_coroutine_sync(device.client.stop_notify(NOTIFY_CHARACTERISTIC))
            
        if self.output_file is not None:
            filename, extension = os.path.splitext(self.output_file)
            counter = 1
            while os.path.exists(os.path.join(self.output_path, self.output_file)):
                self.output_file = f"{filename}_{counter}{extension}"
                counter += 1
        else:
            self.output_file = input(f"Enter the output file name (default: {self.output_file}): ") or self.output_file
        # Save the collected data
        # importlib.reload(self.unify_notifications)
        data_frame = self.unify_notifications()
        self.data_back = data_frame 
        # weak_data_frame = weakref.ref(data_frame)  # weak reference to the data_frame
        data_frame.to_csv(os.path.join(self.output_path, self.output_file), index=False, mode='w')
        
        self.data_back = data_frame 
        
        gc.collect()
        # gc.get_count()
        
        logger.info("Data collection complete.")

    # this end_data_collection method is for streaming data
    def end_data_collection_1(self):
        logger.debug("Disabling notifications.")

        for device in self.connected_devices:
            self.run_coroutine_sync(device.client.stop_notify(NOTIFY_CHARACTERISTIC))
        
        # Save the collected data
        data_frame = self.unify_notifications()

        if self.output_file is not None:
            filename, extension = os.path.splitext(self.output_file)
            # while os.path.exists(os.path.join(self.output_path, self.output_file)):
            self.output_file = f"{filename}{extension}"
        else:
            self.output_file = input(f"Enter the output file name (default: {self.output_file}): ") or self.output_file
        
        data_frame.to_csv(os.path.join(self.output_path, self.output_file), index=False, mode='w')
        logger.info("refreshing data per 2 senconds.")

# *****************************************************
        # data streaming
    def unify_notifications(self):
        all_data = []
        for device in self.connected_devices:
            for _, sensor in device.sensors.items():
                all_data.extend(sensor.data)

        # Create a Pandas DataFrame from the notifications
        df = pd.DataFrame(all_data)

        # We get the highest number of observations per sensor type available. This is used effectively as
        # "sampling rate" in the following transforms
        df.insert(0, "id", range(0, len(df)))
        highest_observation_count = df.groupby(["device", "sensor_type"])["id"].count().max()

        # We compute relative integer ids such that their density spans the highest count, but the observations
        # are set to be more sparse automatically. While this does not track the timestamps perfectly, it allows
        # combining the representation to be more dense. The sampling rates are nearly doubles of each other, which helps.
        df["relative_id"] = df.groupby(["device", "sensor_type"])["id"].transform(
            lambda x: ((x - x.min()) / ((x - x.min()).max()) * highest_observation_count).astype(int))

        # Pivot the DataFrame to get the desired structure
        df_pivot = df.pivot_table(
            index=["relative_id"],
            columns=["device", "sensor_type"],
            values=["timestamp", "sensor_data"],
            aggfunc=lambda x: x,
        ).reset_index()

        # Split the sensor_data columns into separate XYZ columns
        for col in df_pivot.columns:
            if "sensor_data" not in col:
                continue

            if "Acc" in col or "Magn" in col or "Gyro" in col:
                df_pivot[["_".join(col[1:]) + ax for ax in ["_X", "_Y", "_Z"]]] = (df_pivot[col]
                                                                                   .apply(lambda x: pd.Series(x)))
                df_pivot.drop(col, axis=1, inplace=True)
            elif "Temp" in col or "ECG" in col or "HR" in col:
                df_pivot["_".join(col[1:])] = df_pivot[col].apply(lambda x: pd.Series(x))
                df_pivot.drop(col, axis=1, inplace=True)
            elif "IMU6" in col:
                df_pivot[
                    ["_".join(col[1:]) + ax for ax in ["_Acc_X", "_Acc_Y", "_Acc_Z", "_Gyro_X", "_Gyro_Y", "_Gyro_Z"]]] \
                    = df_pivot[col].apply(lambda x: pd.Series(x))
                df_pivot.drop(col, axis=1, inplace=True)
            elif "IMU9" in col:
                df_pivot[["_".join(col[1:]) + ax for ax in
                          ["_Acc_X", "_Acc_Y", "_Acc_Z", "_Gyro_X", "_Gyro_Y", "_Gyro_Z", "_Magn_X", "_Magn_Y",
                           "_Magn_Z"]]] \
                    = df_pivot[col].apply(lambda x: pd.Series(x))
                df_pivot.drop(col, axis=1, inplace=True)

        df_pivot.columns = [' '.join(col).strip() for col in df_pivot.columns.values]

        # Merge the local_timestamp columns
        df_pivot.insert(0, "timestamp", df_pivot.filter(like="timestamp").min(axis=1))
        df_pivot = df_pivot[df_pivot.columns.drop(list(df_pivot.filter(regex="timestamp.+")))]

        # weak_df_pivot = weakref.ref(df_pivot)

        # sort by timestamp
        df_pivot.sort_values(by="timestamp", inplace=True)

        # delete the relative_id column
        df_pivot.drop('relative_id', axis=1, inplace=True)

        # insert the relative_id column
        df_pivot.insert(0, "relative_id", range(0, len(df_pivot)))

        del df, all_data
        gc.collect()
        

        return df_pivot
    
    
        

        return df_pivot
    

    def disconnect_device(self, device_id):
        async def disconnect_coroutine(device_id):
            device = self.connected_devices[device_id]
            logger.info(f"Disconnecting device {device.device.name} ({device.device.address})")
            await device.client.disconnect()
            self.connected_devices.remove(device)

        # Run disconnection coroutine
        self.run_coroutine_sync(disconnect_coroutine(device_id))

    def disconnect_devices(self):
        logger.info("Disconnecting from all MoveSense devices...")

        # Run disconnection coroutines. Repeatedly disconnecting 1st entry since the devices are always popped out of
        # connected devices.
        disconnect_coroutines = [self.disconnect_device(0) for _ in range(len(self.connected_devices))]
        self.run_coroutine_sync(asyncio.gather(*disconnect_coroutines))
