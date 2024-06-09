import struct
import datetime
import numpy as np

from enum import Enum


class MovesenseSensorType(Enum):
    ACCELEROMETER = ('Acc', 3)
    GYROSCOPE = ('Gyro', 3)
    MAGNETOMETER = ('Magn', 3)
    TEMPERATURE = ('Temp', 1)
    ECG = ('ECG', 1)
    HEART_RATE = ('HR', 1)
    IMU6 = ('IMU6', 6)
    IMU9 = ('IMU9', 9)

    def __new__(cls, value, axes):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.axes = axes
        return obj

    @classmethod
    def from_string(cls, value):
        for member in cls:
            if member.value == value:
                return member
            elif value.startswith(member.value):
                return member
            elif value == "IMU":
                return MovesenseSensorType.IMU9
        raise ValueError(f"No member with the value {value} in {cls.__name__}")


class MovesenseSamplingRate(Enum):
    _13_HZ = 13
    _26_HZ = 26
    _52_HZ = 52
    _104_HZ = 104
    _208_HZ = 208
    _416_HZ = 416
    _833_HZ = 833
    _1666_HZ = 1666

    # ECG Sample rates
    _125_HZ = 125
    _128_HZ = 128
    _200_HZ = 200
    _250_HZ = 250
    _256_HZ = 256
    _500_HZ = 500
    _512_HZ = 512

    # None-type for HR and Temperature
    NONE = None

    @classmethod
    def from_int(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"No member with the value {value} in {cls.__name__}")


"""
Acts as an instance for data collection, maintaining the sensor type and unpacking the data appropriately.
Movesense data packets have shape: c c uint32 float32 float32 float32... Where the float sequence is the data.
Depending on the sensor, the data might represent multiple axes. Timestamp is the time of the first data sample.
"""
class MovesenseSensor:
    # 'Serial number' used as an id for the REST path calls
    id_counter = 0

    def __init__(self, sensor_type, sampling_rate):
        # Allow creating from strings, not just enums. Enums simply force typechecking.
        self.sensor_type = sensor_type if sensor_type is MovesenseSensorType \
            else MovesenseSensorType.from_string(sensor_type)
        self.sampling_rate = sampling_rate if sampling_rate is MovesenseSamplingRate \
            else MovesenseSamplingRate.from_int(sampling_rate)

        self.id = MovesenseSensor.id_counter
        MovesenseSensor.id_counter += 1

        # Path which is subscribed to for collecting data from this sensor
        # Same rootpath for everything
        path = f"/Meas/{self.sensor_type.value}"
        if self.sensor_type not in [MovesenseSensorType.HEART_RATE, MovesenseSensorType.TEMPERATURE]:
           # Temp and HR seem to not use sampling rates (which makes sense), so for others, we append the fs.
           path += f"/{self.sampling_rate.value}"
        self.path = (bytearray([1, self.id]) +
                     bytearray(path, "utf-8"))

        self.data = []

    @classmethod
    def from_path(cls, path):
        components = path.split("/")
        sensor_type = components[2]

        if len(components) == 4:
            sampling_rate = int(components[3])
        else:
            sampling_rate = None

        return MovesenseSensor(sensor_type, sampling_rate)

# ****************************************************
    async def notification_handler(self, device_address, data):

        # Unpack the data based on the sensor, ignoring the timestamp and id
        if self.sensor_type == MovesenseSensorType.ECG:
            packet_structure = '<' + ((len(data)-6)//4)*'i'
            data = struct.unpack(packet_structure, data[6:])
        elif self.sensor_type == MovesenseSensorType.HEART_RATE:
            # Heartrate comes without timestamp, but instead, provides average heartrate and
            # rrData (assumed rr-difference).
            # We only really care about the average heartrate so rrData is skipped here.
            packet_structure = '<fh'
            data = struct.unpack(packet_structure, data[2:])[0]
        else:
            packet_structure = '<' + ((len(data)-6)//4)*'f'
            data = struct.unpack(packet_structure, data[6:])

        # Timestamp by arrival time
        local_timestamp = datetime.datetime.now().timestamp()

        # Shape the data
        if self.sensor_type.axes > 1:
            # Data is passed in single array in following structure: sensor, axis, instance.
            # Reshape splits into three axes, split divides it into different sensors, stack to create
            # the full table of instances.
            data = np.hstack(np.split(np.array(data).reshape(-1, 3), self.sensor_type.axes//3))
        else:
            data = np.array(data).reshape(-1, 1)

        if self.sensor_type not in [MovesenseSensorType.TEMPERATURE, MovesenseSensorType.HEART_RATE]:
            # Sampling period
            T_s = 1. / self.sampling_rate.value

            # print(self.sampling_rate.value)
            # print(data.shape[0])

            # Extend timestamp to each instance, starting from past since recorded timestamp is arrival time.
            local_timestamp = np.linspace(-T_s*data.shape[0], 0, data.shape[0]) + local_timestamp

            # Each row should be a new entry, appending in samples to maintain labels.
            # Maybe just refactoring to pands would be more convenient?
            for i, row in enumerate(data):
                sample = {
                    "timestamp": local_timestamp[i],
                    "device": device_address,
                    "sensor_type": self.sensor_type.value,
                    "sensor_data": row,
                }
                self.data.append(sample)
        else:
            # HR and Temp yield only one sample
            sample = {
                "timestamp": local_timestamp,
                "device": device_address,
                "sensor_type": self.sensor_type.value,
                "sensor_data": data[0],
            }
            self.data.append(sample)

