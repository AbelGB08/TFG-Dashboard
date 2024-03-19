#!/usr/bin/env python3

import logging
from ina226 import INA226
from time import sleep
import requests


WEATHSTONE_IMPUT_VOLTAGE = 12

MAX_SENSOR_VOLT_PERCENTAGE = 0.45833333

SENSORS_DATA = {
    "INA1": 0x40,
    "INA2": 0x41,
    "INA3": 0x42,
    "INA4": 0x43,
    "INA5": 0x44
}

SENSORS = []

temp_sensor_id = "28-3de10457dc9a"

def init_sensors():
    for sensor_name, address in SENSORS_DATA.items():
        try:
            sensor = INA226(busnum=1, address=address, max_expected_amps=20, shunt_ohms=0.002, log_level=logging.DEBUG)
            sensor.configure()
            SENSORS.append((sensor_name, sensor))
            #updateSensorStatus(sensor_name, "OK", "Sensor initialized correctly")
        except Exception as e:
            #updateSensorStatus(sensor_name, "ERROR", "Could not initialize sensor")
            print(f"INIT ERROR for {sensor_name}: {e}")

def writeInDB(voltage, amps, power, sensorName):
    url = "http://localhost:5000/insertData/" + str(voltage/1000) + "/" + str(amps/1000) + "/" + str(power/1000) + "/" + sensorName
    requests.post(url)

def writeTempInDB(temp, sensorName):
    url = "http://localhost:5000/insertTemp/" + str(temp) + "/" + sensorName
    requests.post(url)

def updateSensorStatus(sensorName, status, message):
    url = "http://localhost:5000/updateSensorStatus/" + sensorName + "/" + status + "/" + message
    requests.get(url)

def read(sensor, sensorName):
    v = round(sensor.voltage(), 3) * 1000
    print("\r                                                                                               ", end="", flush=True)
    print("\r (" + str(round((v/(WEATHSTONE_IMPUT_VOLTAGE * MAX_SENSOR_VOLT_PERCENTAGE))*100, 1)) + "%%) Voltage:\t%.3f" % sensor.voltage() + " mV\t|\t", end="", flush=True)
    print("Amps:\t%.3f" % sensor.current() + " mAh\t|\t", end="", flush=True)
    #print("Supply V: " + str(ina.supply_voltage()) + " mV  |  ", end="", flush=True)
    #print("Shunt V: " + str(ina.shunt_voltage()) + " mV  |  ", end="", flush=True)
    print("Power:\t%3.f" % sensor.power() + " mW", end="", flush=True)
    print(" --- " + sensorName)
    writeInDB(v, sensor.current(), sensor.power(), sensorName)
    sleep(0.05)


if __name__ == "__main__":
    init_sensors()
    sleep(0.2)
    while True:
        print (SENSORS)
        for sensor_name, sensor in SENSORS:
            if sensor.is_conversion_ready():
                print("==============================================================================================================================")
                read(sensor, sensor_name)
                print("==============================================================================================================================")