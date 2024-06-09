import sys
import re
import asyncio

from src.movesense.movesense_sensor import MovesenseSensor
from src.movesense.movesense_device_manager import MovesenseDeviceManager
from src.movesense import movesense_device_manager

import logging
import time

import socket
import threading
import queue
import os

import gc
import importlib

logger = logging.getLogger("__main__")

# **********************************************************************
class MovesenseCLI:
    def __init__(self, config=None):
        self.config = config or {}

        self.device_manager = MovesenseDeviceManager(config)
        self.output_filename = None

    def display_menu(self):
        logger.info("==== Movesense CLI Menu ====")
        logger.info("1. Start Data Collection")
        logger.info("2. Start Streaming Data Collection")
        logger.info("3. Connect to an Additional Device")
        logger.info("4. Configure Connected Devices")
        logger.info("5. Save Current Configuration")
        logger.info("6. Exit")

    def display_menu_remote(self):
        logger.info("==== Movesense CLI Menu ====")
        logger.info("0. End Remote Data Collection")
        logger.info("1. Start Remote Data Collection")
        logger.info("2. Start Data Collection")
        logger.info("3. Start Streaming Data Collection")
        logger.info("4. Connect to an Additional Device")
        logger.info("5. Configure Connected Devices")
        logger.info("6. Save Current Configuration")
        logger.info("7. Exit")

    def start_device_connection_activity(self):
        found_devices = self.device_manager.get_available_devices()

        if not found_devices:
            logger.warning("No MoveSense devices found. Make sure that the MoveSense devices are turned on, and not "
                           "connected to another device.")
            return
        else:
            logger.info("Select the MoveSense Device to connect to (list-id or mac-address)")
            choice = input()

            # Regex match for MAC address input (MAC address regex)
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", choice.lower()):
                # Find the device with the specified MAC address
                selected_device = next(
                    (device for device in found_devices if device.device.address.lower() == choice.lower()),
                    None)

                if selected_device:
                    try:
                        self.device_manager.connect(selected_device)
                        if "devices" in self.config:
                            self.config["devices"].append({"address": selected_device, "paths": []})
                        else:
                            self.config["devices"] = [{"address": selected_device, "paths": []}]
                        logger.info(f"Connected to device with MAC address: {selected_device.device.device.address}")
                    except Exception as e:
                        logger.error(
                            f"Failed to connect to device with MAC address '{selected_device.device.device.address}': {e}")
                else:
                    logger.warning(f"No device found with MAC address '{choice}'")

            else:
                try:
                    index = int(choice) - 1
                    self.device_manager.connect(found_devices[index])
                    if "devices" in self.config:
                        self.config["devices"].append({"address": found_devices[index].address, "paths": []})
                    else:
                        self.config["devices"] = [{"address": found_devices[index].address, "paths": []}]

                    logger.info(
                        f"Connected to device with list-id: {index + 1}, and MAC address: {found_devices[index].address}")
                except ValueError:
                    logger.error(f"Invalid input. Please enter a valid list-id as an integer or a MAC address.")
                except IndexError:
                    logger.error(f"Invalid list-id '{index}'. List-id out of range.")
                except Exception as e:
                    logger.error(f"Unknown device-id '{choice}'. Failed to connect: {e}")

    def start_device_configuration_activity(self):

        if not self.device_manager.connected_devices:
            logger.warning("No connected devices found")
            return

        try:
            while True:
                logger.info("Select the device to configure. 'return' to exit back to main menu.")
                self.device_manager.show_connected_devices()

                choice = input()

                if choice == "return":
                    raise KeyboardInterrupt
                selected_device = None
                # If choice based on MAC (MAC address regex)
                if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", choice.lower()):
                    selected_device = next((device for device in self.device_manager.connected_devices
                                            if device.device.address.lower() == choice.lower()),
                                           None)
                # If choice based on list id
                else:
                    try:
                        index = int(choice) - 1
                        selected_device = self.device_manager.connected_devices[index]
                    except ValueError:
                        logger.error(f"Invalid input. Please enter a valid list-id as an integer or a MAC address.")
                    except IndexError:
                        logger.error(f"Invalid list-id '{index + 1}'. List-id out of range.")

                # Show configuration menu
                self.start_single_device_configuration(selected_device)

        except KeyboardInterrupt:
            logger.info("Exiting the device menu")

    def start_single_device_configuration(self, device):
        try:
            while True:
                logger.info("What would you like to do?")
                logger.info("1. Rename the device")
                logger.info("2. Subscribe to Acceleration")
                logger.info("3. Subscribe to Gyroscope")
                logger.info("4. Subscribe to Magnetometer")
                logger.info("5. Subscribe to Temperature")
                logger.info("6. Subscribe to ECG")
                logger.info("7. Subscribe to IMU6")
                logger.info("8. Subscribe to IMU9")
                logger.info("9. Return")

                choice = input()

                if choice == "1":
                    logger.info("Rename the device")
                    choice = input("New device name:")
                    self.device_manager.rename_device(device, choice)
                elif choice == "9":
                    raise KeyboardInterrupt
                elif choice in list(map(lambda x: str(x), range(2, 8 + 1))):
                    sensor_full = ["Acceleration", "Gyroscope", "Magnetometer", "Temperature", "ECG", "IMU6", "IMU9"][
                        int(choice) - 2]
                    msg = "Subscribe to " + sensor_full
                    logger.info(msg)

                    try:
                        logger.info("Choose the sampling rate (13, 26, 52, 104, 208, 416, 833, 1666) ")
                        fs = int(input())
                        # Subscription path determines response id (fixed for ease of use), "Meas", the sensor type,
                        # and sampling rate
                        sensor = MovesenseSensor(sensor_full, fs)

                        for config in self.config["devices"]:
                            if config["address"] == device.device.address:
                                config["paths"].append(
                                    f"Meas/{sensor.sensor_type.value}/{sensor.sampling_rate.value}")

                        # self.config["devices"]["paths"].append(  # there has an error: TypeError: list indices must be integers or slices, not str
                        #     f"Meas/{sensor.sensor_type.value}/{sensor.sampling_rate.value}")
                        self.device_manager.subsribe_to_sensor(device, sensor)
                    except ValueError:
                        logger.error(f"Invalid input. Please enter a valid integer choice.")
                

        except KeyboardInterrupt:
            logger.info("Exiting the device configuration")

    def start_collection_activity(self):
        logger.info("Starting data collection. Press ctrl+c to terminate")
        self.device_manager.start_data_collection_sync()

        try:
            asyncio.get_event_loop().run_until_complete(
                asyncio.Event().wait())  # Wait indefinitely until the event is set
        except KeyboardInterrupt:
            logger.info("Ending data collection, saving...")
        finally:
            self.device_manager.end_data_collection()

    def start_collection_activity_online(self):
        logger.info("Starting data collection. This is streaming model.")
        self.device_manager.start_data_collection_sync()
        gc.collect()

    def end_collection_activity_online(self):
        logger.info("Ending data collection, saving...")
        self.device_manager.end_data_collection()
        # del movesense_device_manager.MovesenseDeviceManager.unify_notifications
        # importlib.reload(movesense_device_manager)
        gc.collect()
            
    # def start_collection_activity(self, input_queue):
    
    #     logger.info("Starting data collection. receiving control bit '1/0' from the server")
    #     self.device_manager.start_data_collection_sync()

    #     try:
    #         asyncio.get_event_loop().run_until_complete(asyncio.Event().wait())  # Wait indefinitely until the event is set

    #     except self.get_signals(input_queue) == "0":
        
    #         logger.info("Ending data collection, saving...")
    #     finally:
    #         self.device_manager.end_data_collection()
            
    # async def data_collection_loop(self, input_queue):
    #     # This coroutine combines data collection start and checking for the end signal of data collection
    #     logger.info("Starting data collection. receiving control bit '1/0' from the server")
    #     self.device_manager.start_data_collection_sync()

    #     # Loop until the end signal is received
    #     while not await self.get_signals_sync(input_queue):
    #         await asyncio.sleep(5e-3)  # Sleep for a short time to avoid busy waiting
        
    #     logger.info("Ending data collection, saving...")
    #     self.device_manager.end_data_collection()


    # def start_collection_activity(self, input_queue):
    #     # This function starts the data collection loop
    #     loop1 = asyncio.get_event_loop()
    #     try:
    #         loop1.run_until_complete(self.data_collection_loop(input_queue))
    #     except Exception as e:
    #         logger.error(f"An error occurred: {e}")

    

    # streaming data collection_activity_1
    def start_collection_activity_1(self):
        logger.info("Starting data collection. This is streaming model.")
        
        while True:
            self.device_manager.start_data_collection_sync_1()
            time.sleep(2)
            
            # time.sleep(4)

            # try:
            #     asyncio.get_event_loop().run_until_complete(
            #         asyncio.Event().wait())  # Wait indefinitely until the event is set
            # except KeyboardInterrupt:
            #     logger.info("Ending data collection, saving...")
            # finally:
            #     self.device_manager.end_data_collection()  
            #     break
            self.device_manager.end_data_collection_1()

 ############This is the function for listening to the signals from the server################

    def listen_for_signals(self, input_queue, port):
        host = '192.168.1.137'

        server = ('192.168.1.137', 5000)

        c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        c.bind((host, port))

        while True:
            # recv data from client
            data, addr = c.recvfrom(1024)
            data = data.decode('utf-8')
            print("server address:"+ str(addr) +",client address:" + host + ":" + str(port))
            print("Received from server: " + data)
            c.sendto(data.encode('utf-8'), server)
            if not data:
                break  # Break the loop if no data is received
            
            user_input = data.strip()
            input_queue.put(user_input)

############This is the function for getting the signals from the server################
    def get_signals(self, input_queue):
        
        control_bit = input_queue.get_nowait()
        return control_bit

############This is the synchronous get function waiting the queue signal from the server################    
    async def get_signals_sync(self, input_queue):
        # This coroutine listens for signals from the server
        control_bit = input_queue.get_nowait()
        return control_bit
    
    def thread_initialization(self, port):
        # Input queue for receiving signals from the server
        input_queue = queue.Queue()
        # start the thread for listening for signals
        input_thread = threading.Thread(target=self.listen_for_signals, args=(input_queue,port,))
        input_thread.daemon = True
        input_thread.start()
        return input_queue, input_thread
    

    def run_remote(self):
        port = 7000
        input_queue, input_thread = self.thread_initialization(port)

        self.display_menu_remote()
        while True:
            
            # self.display_menu()
            try:
                choice = self.get_signals(input_queue)
               
                if choice == "0":
                    self.end_collection_activity_online()
                elif choice == "1":
                    self.start_collection_activity_online()
                elif choice == "2":
                    self.start_collection_activity()
                elif choice == "3":
                    self.start_collection_activity_1()
                elif choice == "4":
                    self.start_device_connection_activity()
                elif choice == "5":
                    self.start_device_configuration_activity()
                elif choice == "6":
                    pass
                elif choice == "7" or choice.lower() == "exit":
                    logger.info("Exiting MoveSense CLI. Goodbye.")
                    self.device_manager.disconnect_devices()
                    break
                else:
                    logger.warning(f"Unrecognized selection {choice}")

            except queue.Empty:
                pass

            # except KeyboardInterrupt:
            #     logger.info("Exiting MoveSense CLI. Goodbye.")
            #     self.device_manager.disconnect_devices()
            #     break
            except Exception as e:
                logger.error(f"An error occurred: {e}")

    def run(self):
        while True:
            self.display_menu()
            choice = input()

            if choice == "1":
                self.start_collection_activity()
            elif choice == "2":
                self.start_collection_activity_1()
            elif choice == "3":
                self.start_device_connection_activity()
            elif choice == "4":
                self.start_device_configuration_activity()
            elif choice == "5":
                pass
            elif choice == "6" or choice.lower() == "exit":
                logger.info("Exiting MoveSense CLI. Goodbye.")
                self.device_manager.disconnect_devices()
                break
            else:
                logger.warning(f"Unrecognized selection {choice}")


if __name__ == "__main__":
    movesense_cli = MovesenseCLI()
    # movesense_cli.run()
    movesense_cli.run_remote()
    # movesense_cli.run_remote()
