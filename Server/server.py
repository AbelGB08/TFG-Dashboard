from flask import Flask, request, render_template, jsonify, redirect, send_from_directory
from flask_socketio import SocketIO
from tinydb import TinyDB, Query
from datetime import datetime
from threading import Thread
import json
import os

if not os.path.exists('./database'):
    os.makedirs('./database')

bateries = TinyDB('./database/bateries.json')
temperature = TinyDB('./database/temperature.json')
victron = TinyDB('./database/victron.json')
shadowBaseCurrents = TinyDB('./database/shadowBaseCurrents.json')
shadowBaseTemperatures = TinyDB('./database/shadowBaseTemperatures.json')
logs = TinyDB('./database/logs.json')

# Mapear los tipos de sensores con sus bases de datos y los campos que deben usarse
sensor_config = {
    "INA": {
        "db": bateries,
        "fields": ["volts", "amps", "pow"],
    },
    "BT": {
        "db": temperature,
        "fields": ["base", "chimenea", "exterior", "bandeja"],
    },
    "SBC": {
        "db": shadowBaseCurrents,
        "fields": ["amps1", "amps2", "amps3", "amps4"],
    },
    "SBT": {
        "db": shadowBaseTemperatures,
        "fields": ["temp1", "temp2", "temp3", "temp4"],
    },
}

# Obtener los limites de los sensores
with open('./sensor_limits.json') as f:
    sensor_limits = json.load(f)

app = Flask(__name__)
socketio = SocketIO(app)

DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

def sendLogIfExceedsLimits(sensor, valueType, value, limits):
    if int(value) > limits["upper_limit"]:
        sendLog({
            "sensor": sensor,
            "valueType": valueType,
            "value": value
        })
    elif int(value) < limits["lower_limit"]:
        sendLog({
            "sensor": sensor,
            "valueType": valueType,
            "value": value
        })

    logs.insert({
        "sensor": sensor,
        "valueType": valueType,
        "value": value,
        "date": datetime.now().strftime(DATE_FORMAT)
    })

@app.route('/')
def index():
    return redirect('/live')

@app.route('/live')
def live():
    return render_template("live.html")

@app.route('/search')
def search():
    return render_template("index.html")

@app.route('/getData', methods=['GET'])
def getData():
    startDate = formatDate(request.args.get('startDate'))
    endDate = formatDate(request.args.get('endDate'))
    sensorName = request.args.get('sensorName')

    data = Query()

    # Identificar tipo de sensor y extraer configuración
    if sensorName.startswith("INA"):
        sensor_key = sensorName[:3]
        query_condition = (data.date >= startDate) & (data.date <= endDate) & (data.sensor == sensorName)
    else:
        sensor_key = sensorName
        query_condition = (data.date >= startDate) & (data.date <= endDate)

    config = sensor_config.get(sensor_key)

    if not config:
        return jsonify(message="Invalid sensor name", data=[]), 400

    # Obtener los datos solicitados
    results = config["db"].search(query_condition)

    # Inicializar los campos de la respuesta
    response = {field: [] for field in config["fields"]}
    response["dates"] = []

    # Añadir los datos a la respuesta
    for result in results:
        for field in config["fields"]:
            response[field].append(result.get(field, None))
        response["dates"].append(result["date"])

    # Crear una lista de listas con los datos y las fechas para devolverla en la respuesta
    response_list = [response[field] for field in config["fields"]] + [response["dates"]]

    return jsonify(message="GET DATA RESPONSE", data=response_list)

@app.route('/insertData/<volts>/<amps>/<pow>/<sensor>', methods=['POST'])
def insertData(volts=0, amps=0, pow=0, sensor="*"):
    data = {
        "volts": volts,
        "amps": amps,
        "pow": pow,
        "date": datetime.now().strftime(DATE_FORMAT),
        "sensor": sensor
    }

    handleUpdateChart(data)

    try:
        dbCount = bateries.insert(data)
    except Exception as e:
        return jsonify(message="Database error", error=str(e)), 500

    sendLogIfExceedsLimits(sensor, "Amps", amps, sensor_limits[sensor]["amps"])
    sendLogIfExceedsLimits(sensor, "Volts", volts, sensor_limits[sensor]["volts"])
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertTemp/<temp1>/<temp2>/<temp3>/<temp4>', methods=['POST'])
def insertTemp(temp1=0, temp2=0, temp3=0, temp4=0):
    data = {
        "base": temp1,
        "chimenea": temp2,
        "exterior": temp3,
        "bandeja": temp4,
        "date": datetime.now().strftime(DATE_FORMAT),
        "sensor": "temps"
    }

    handleUpdateChart(data)

    try:
        dbCount = temperature.insert(data)
    except Exception as e:
        return jsonify(message="Database error", error=str(e)), 500

    for field in ["base", "chimenea", "exterior", "bandeja"]:
        sendLogIfExceedsLimits("BT", field.capitalize() + " Temp", data[field], sensor_limits["BT"][field])
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertVictronVoltage/', methods=['POST'])
def insertVictron(volts=0):
    data = request.json
    print(data)

    handleUpdateChart(data)
    
    dbCount = victron.insert(data[0])
    # if dbCount > 100:
        # victron.truncate()
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertCurrentShadowBase/<curr1>/<curr2>/<curr3>/<curr4>', methods=['POST'])
def insertCurrentShadowBase(curr1=0, curr2=0, curr3=0, curr4=0):
    data = {
        "amps1": curr1,
        "amps2": curr2,
        "amps3": curr3,
        "amps4": curr4,
        "date": datetime.now().strftime(DATE_FORMAT),
        "sensor": "sbc"
    }

    handleUpdateChart(data)

    try:
        dbCount = shadowBaseCurrents.insert(data)
    except Exception as e:
        return jsonify(message="Database error", error=str(e)), 500

    for field in ["amps1", "amps2", "amps3", "amps4"]:
        sendLogIfExceedsLimits("SBC", field.capitalize(), data[field], sensor_limits["SBC"]["amps"])
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertTemperatureShadowBase/<temp1>/<temp2>/<temp3>/<temp4>', methods=['POST'])
def insertTemperatureShadowBase(temp1=0, temp2=0, temp3=0, temp4=0):
    data = {
        "temp1": temp1,
        "temp2": temp2,
        "temp3": temp3,
        "temp4": temp4,
        "date": datetime.now().strftime(DATE_FORMAT),
        "sensor": "sbt"
    }

    handleUpdateChart(data)

    try:
        dbCount = shadowBaseTemperatures.insert(data)
    except Exception as e:
        return jsonify(message="Database error", error=str(e)), 500

    for field in ["temp1", "temp2", "temp3", "temp4"]:
        sendLogIfExceedsLimits("SBT", field.capitalize(), data[field], sensor_limits["SBT"][field])
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/database/logs.json')
def getLogs():
    logs_dir = './database'
    logs_file = 'logs.json'

    try:
        return send_from_directory(directory=logs_dir, path=logs_file, as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "logs.json not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def formatDate(date):
    date = date.split('T')
    fullDay = date[0].split('-')
    hour = date[1]

    return fullDay[2] + '-' + fullDay[1] + '-' + fullDay[0] + ' ' + hour

def handleUpdateTemp(sensor, temperatura):
    # Transmite la temperatura actualizada a todos los clientes conectados
    socketio.emit('update_temp', {'id': sensor, 'temp': temperatura})

def handleUpdateChart(data):
    socketio.emit('update_chart', data)

def sendLog(logData):
    socketio.emit('log', {
        'sensor': logData["sensor"],
        'date': datetime.now().strftime(DATE_FORMAT),
        'message': "Sensor " + logData["sensor"] + " has exceeded the limit: " + logData["valueType"] + " = " + str(logData["value"])
    })

socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
#app.run(host='0.0.0.0', port=8000, debug=True)