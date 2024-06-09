# MoveSense Data Collector

## Description

MoveSense Data Collection is a Python-based command-line tool for collecting sensor data from MoveSense devices. It 
utilizes the Bleak library for Bluetooth communication and provides a customizable framework for connecting to multiple 
devices, subscribing to sensor data, and collecting and saving data in real-time.

Most of the MoveSense libraries offer data collection via mobile apps. This program aims to offer the same functionality
on desktop devices, with ease of connectivity to multiple devices and combining the collected data into single file.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Firmware Installation](#firmware-installation)
- [Contributing](#contributing)
- [Issues](#issues)
- [WIP Tasks](#wip-tasks)

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/yzy1997/multi-model-data-collector.git
    ```

2. Navigate to the project directory:

    ```bash
    cd multi-model-data-collector
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start data collection using the CLI, follow these steps:

1. Ensure that MoveSense devices are turned on and discoverable.

2. (Optional) Create a session configuration file specifying the data output path, the devices and sensor paths.

    ```yaml
    output:
      path: outputs # Folder to which the data should be saved to
      filename:     # Filename template, which will be extended with
                    # a number when multiple data collections are done
   devices:         # List of adress-path objects.
   - address: 00:00:00:00:00:00 # MoveSense device address
      paths:                     # List of sensor paths to subscribe to
      - /Meas/Acc/13             # Find more details in MoveSense
                                 # official documentation.
    ```

3. Run the CLI, `--session` argument specifies the location of session config. If not provided
the CLI will look for "session.yaml" from root. If not found, a plain, empty session is initialized. Devices can be
connected to and paths subscribed to during runtime.

    ```bash
    python3 -m main  --session "session.yaml"
    ```

4. Follow the on-screen instructions to start and end data collection.

## Firmware Installation

For this CLI, the MoveSense devices require the `custom-gattsvc-app` firmware.

Official instructions for firmware update can be found here:
- [MoveSense Firmware Installation Guide](https://www.movesense.com/docs/test_env/esw/dfu_update/)

The firmware installation requires a phone with the showcase app:
- [MoveSense ShowcaseApp Downloads](https://bitbucket.org/movesense/movesense-mobile-lib/downloads/)

And the firmware zip-file from:
- [MoveSense Firmware Downloads](https://bitbucket.org/movesense/movesense-device-lib/src/master/samples/bin/release/)

## Contributing

Collaborations appreciated, either via forks and pull-requests, or as direct members to the project. Check the
issue-list, or add to it for missing features.

## Issues

If you encounter any issues or have suggestions for improvements, please open an issue on the GitHub repository.

Currently, the largest issues are listed below, but basic functionality of the CLI is complete. 

## WIP Tasks

- [ ] (Bug) Async issue on disconnecting all devices, causes a crash on exit.
- [x] ~~(Bug) Can not change sampling rate of individual devices via MoveSense REST-API. Another path required?~~
- [x] ~~Due to above, data collection with multiple mismatching framerates not tested.~~
- [ ] (Feature) Session configs should be made saveable, when edited during runtime.
- [x] ~~(Refactor) The sensor id's for BLE are currently hard-coded. Different structure would be better.~~

## Contributors

Big thanks to anyone considering helping out with this!