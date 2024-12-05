from flask import Flask, request, render_template, jsonify, redirect
from flask_socketio import SocketIO
from tinydb import TinyDB, Query
from datetime import datetime
from time import sleep
from threading import Thread

bateries = TinyDB('./database/bateries.json')
temperature = TinyDB('./database/temperature.json')
victron = TinyDB('./database/victron.json')
shadowBaseCurrents = TinyDB('./database/shadowBaseCurrents.json')
shadowBaseTemperatures = TinyDB('./database/shadowBaseTemperatures.json')

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

app = Flask(__name__)
socketio = SocketIO(app)

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
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "sensor": sensor
    }

    handle_update_chart(data)

    dbCount = bateries.insert(data)
    # if dbCount > 10000:
    #     bateries.truncate()
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertTemp/<temp1>/<temp2>/<temp3>/<temp4>', methods=['POST'])
def insertTemp(temp1=0, temp2=0, temp3=0, temp4=0):
    data = {
        "base": temp1,
        "chimenea": temp2,
        "exterior": temp3,
        "bandeja": temp4,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    data["sensor"] = "temps"

    handle_update_chart(data)
    
    dbCount = temperature.insert(data)
    # if dbCount > 100:
        # temperature.truncate()
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertVictronVoltage/', methods=['POST'])
def insertVictron(volts=0):
    data = request.json
    print(data)

    handle_update_chart(data)
    
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
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    data["sensor"] = "sbc"

    dbCount = shadowBaseCurrents.insert(data)
    # if dbCount > 100:
        # temperature.truncate()

    handle_update_chart(data)
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertTemperatureShadowBase/<temp1>/<temp2>/<temp3>/<temp4>', methods=['POST'])
def insertTemperatureShadowBase(temp1=0, temp2=0, temp3=0, temp4=0):
    data = {
        "temp1": temp1,
        "temp2": temp2,
        "temp3": temp3,
        "temp4": temp4,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    data["sensor"] = "sbt"

    dbCount = shadowBaseTemperatures.insert(data)
    # if dbCount > 100:
        # temperature.truncate()
    
    handle_update_chart(data)
    
    return jsonify(message="NEW DATA INSERTED", data=data)

'''
@app.route('/updateStatusSection')
def updateStatusSection():
    return status.all()

@app.route('/updateSensorStatus/<sensorName>/<statusName>/<message>')
def updateSensorStatus(sensorName="", statusName="", message=""):
    print(sensorName + "---" + statusName)
    sensor = Query()
    status.update({'status': statusName, 'message': message}, sensor.name == sensorName)
'''

def formatDate(date):
    date = date.split('T')
    fullDay = date[0].split('-')
    hour = date[1]

    return fullDay[2] + '-' + fullDay[1] + '-' + fullDay[0] + ' ' + hour

def handle_update_temp(sensor, temperatura):
    # Transmite la temperatura actualizada a todos los clientes conectados
    socketio.emit('update_temp', {'id': sensor, 'temp': temperatura})

def handle_update_chart(data):
    socketio.emit('update_chart', data)

def sendLog():
    socketio.emit('log', {
        'date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        'message': "Lorem ipsum dolor sit amet consectetur adipiscing elit, phasellus pellentesque semper sodales odio dui curabitur enim, ac tortor tellus non sociosqu auctor. Semper ornare et potenti cubilia dictumst ante libero lacus, vitae sollicitudin iaculis curae congue sagittis feugiat, aliquet aptent consequat mus eros pretium massa. Interdum dui nulla feugiat ligula quisque facilisis dis sociosqu aptent lacus rutrum ac morbi urna augue, quam sapien pretium curabitur sociis dignissim suscipit id tristique odio posuere penatibus montes."
    })

def sendLog2():
    while True:
        print("===== Sending log =====")
        sendLog()
        sleep(10)

th = Thread(target=sendLog2)
th.daemon = True
th.start()

socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
#app.run(host='0.0.0.0', port=8000, debug=True)