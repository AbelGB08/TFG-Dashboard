#!/usr/bin/env python3
import logging
from ina226 import INA226
from time import sleep
import mariadb
import requests

mydb = mariadb.connect (
        host="localhost",
        user="AbelGB08",
        password="agb08",
        database="ina226testdb"
)

mycursor = mydb.cursor()

WEATHSTONE_IMPUT_VOLTAGE = 12

MAX_SENSOR_VOLT_PERCENTAGE = 0.45833333

def writeInDB(voltage, amps, power, sensorName):
    url = "http://192.168.1.81:8000/insertData/" + str(voltage) + "/" + str(amps) + "/" + str(power) + "/" + sensorName
    response = requests.get(url)

def read():
    """
    print("Bus Voltage    : %.3f V" % ina.voltage())
    print("Bus Current    : %.3f mA" % ina.current())
    print("Supply Voltage : %.3f V" % ina.supply_voltage())
    print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
    print("Power          : %.3f mW" % ina.power())
    """

    v = round(ina.voltage(), 3)
    print("\r                                                                                                 ", end="", flush=True)
    print("\r (" + str(round((v/(WEATHSTONE_IMPUT_VOLTAGE * MAX_SENSOR_VOLT_PERCENTAGE))*100, 1)) + "%%) Voltage:\t%.3f" % ina.voltage() + " mV\t|\t", end="", flush=True)
    print("Amps:\t%.3f" % ina.current() + " mAh\t|\t", end="", flush=True)
    #print("Supply V: " + str(ina.supply_voltage()) + " mV  |  ", end="", flush=True)
    #print("Shunt V: " + str(ina.shunt_voltage()) + " mV  |  ", end="", flush=True)
    print("Power:\t%3.f" % ina.power() + " mW", end="", flush=True)
    writeInDB(ina.voltage(), ina.current(), ina.power(), "Ina3")
    sleep(0.05)


if __name__ == "__main__":
    ina = INA226(busnum=1, max_expected_amps=20, shunt_ohms=0.002, log_level=logging.DEBUG)
    ina.configure()
    #ina.set_low_battery(5)
    sleep(3)
    print("\n======================= Sensor 1 =======================")
    read()
    sleep(2)
    '''
    print("===================================================Begin to reset")
    ina.reset()
    sleep(5)
    ina.configure()
    ina.set_low_battery(3)
    sleep(5)
    print("===================================================Begin to sleep")
    ina.sleep()
    sleep(2)
    print("===================================================Begin to wake")
    ina.wake()
    sleep(0.2)
    print("===================================================Read again")
    read()
    sleep(5)
    print("===================================================Trigger test")
    '''
    ina.wake(3)
    sleep(0.2)
    while True:
        ina.wake(3)
        #sleep(3)
        while 1:
            if ina.is_conversion_ready():
                #sleep(3)
                #print("===================================================Conversion ready")
                read()
                sleep(10)
                break
        #sleep(1)
        #print("===================================================Trigger again")
