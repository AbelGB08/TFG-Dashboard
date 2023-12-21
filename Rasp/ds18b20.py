import os
from time import sleep
from datetime import datetime
from tinydb import TinyDB, Query
import requests

temperatureDB = TinyDB('temperature.json')

# Definir la ruta del directorio de los sensores DS18B20
sensor_directory = '/sys/bus/w1/devices/'

def insertTemp(temp=0, sensor="ds18b20"):
    dbCount = temperatureDB.insert({
        "temp": temp,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "sensor": sensor
    })

    if dbCount > 100:
        temperatureDB.truncate()

def writeTempInDB(temp, sensorName):
    url = "http://192.168.1.71:8000/insertTemp/" + str(temp) + "/" + sensorName
    requests.get(url)

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
sensor_id = "28-3de10457dc9a"

def temperature_proc(sensor_id):
	# Leer la temperatura y mostrarla
	temperature = read_temperature(sensor_id)
	if temperature is not None:
		#insertTemp(temp=temperature)
		writeTempInDB(temperature, "TempSens1")
		print(f"Temperatura: {temperature} ºC", end="\r")
	else:
		print("No se pudo leer la temperatura.")
