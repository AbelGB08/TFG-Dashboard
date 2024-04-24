#!/usr/bin/python

import os
from time import sleep
from datetime import datetime
from tinydb import TinyDB, Query
import requests

#temperatureDB = TinyDB('temperature.json')

# Definir la ruta del directorio de los sensores DS18B20
sensor_directory = '/sys/bus/w1/devices/'

# def insertTemp(temp=0, sensor="ds18b20"):
#     dbCount = temperatureDB.insert({
#         "temp": temp,
#         "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
#         "sensor": sensor
#     })

#     if dbCount > 100:
#         temperatureDB.truncate()

def writeTempInDB(temp1, temp2, temp3, temp4):
    url = "http://localhost:5000/insertTemp/" + str(temp1) + "/" + str(temp2) + "/" + str(temp3) + "/" + str(temp4)
    requests.post(url)

# Función para leer la temperatura desde un sensor DS18B20
def read_temperature(sensor_id):
    try:
        # Construir la ruta completa al archivo que contiene la temperatura
        sensor_file = os.path.join(sensor_directory, sensor_id, 'w1_slave')

        # Leer el archivo
        with open(sensor_file, 'r') as file:
            lines = file.readlines()

        # Extraer la temperatura en ºC
        temperature_line = lines[1]
        temperature_data = temperature_line.split('=')[1]
        temperature_celsius = float(temperature_data) / 1000.0

        return temperature_celsius

    except Exception as e:
        print(f"Error al leer el sensor: {str(e)}")
        return None

# Listar los sensores conectados: ls /sys/bus/w1/devices/
sensor_id1 = "28-3ce104571023"
sensor_id2 = "28-3ce104571b69"
sensor_id3 = "28-3ce10457c7cf"
sensor_id4 = "28-3ce10457e22d"

if __name__ == "__main__":
     while True:
        # Leer la temperatura y mostrarla
        temperature1 = read_temperature(sensor_id1)
        temperature2 = read_temperature(sensor_id2)
        temperature3 = read_temperature(sensor_id3)
        temperature4 = read_temperature(sensor_id4)
        if temperature1 is not None and temperature2 is not None and temperature3 is not None and temperature4 is not None:
            writeTempInDB(temperature1, temperature2, temperature3, temperature4)
            print(f"Temperatura: {temperature1} ºC", end="\r")
        else:
            print("No se pudo leer la temperatura.")

        sleep(2)
