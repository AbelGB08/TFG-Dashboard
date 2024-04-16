from flask import Flask, request, render_template, jsonify, redirect
from flask_socketio import SocketIO
from tinydb import TinyDB, Query
from datetime import datetime

bateries = TinyDB('bateries.json')
temperature = TinyDB('temperature.json')
victron = TinyDB('victron.json')
shadowBase = TinyDB('shadowBase.json')

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
def getData(startDate='a', endDate='b', sensorName="*"):
    startDate = formatDate(request.args.get('startDate'))
    endDate = formatDate(request.args.get('endDate'))
    sensorName = request.args.get('sensorName')
    
    data = Query()
    results = bateries.search((data.date >= startDate) & (data.date <= endDate) & (data.sensor == sensorName))

    volts = []
    amps = []
    pow = []
    dates = []
    for result in results:
        volts.append(result["volts"])
        amps.append(result["amps"])
        pow.append(result["pow"])
        dates.append(result["date"])

    return render_template("index.html", dates=dates, volts=volts, amps=amps, pow=pow, sensor=sensorName)

@app.route('/insertData/<volts>/<amps>/<pow>/<sensor>', methods=['POST'])
def insertData(volts=0, amps=0, pow=0, sensor="*"):
    data = {
        "volts": volts,
        "amps": amps,
        "pow": pow,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "sensor": sensor
    }
    dbCount = bateries.insert(data)

    handle_update_chart(data)

    if dbCount > 100:
        bateries.truncate()
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertTemp/<temp1>/<temp2>/<temp3>/<temp4>/', methods=['POST'])
def insertTemp(temp1=0, temp2=0, temp3=0, temp4=0):
    data = {
        "base": temp1,
        "chimenea": temp2,
        "exterior": temp3,
        "bandeja": temp4,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    dbCount = temperature.insert(data)

    data["sensor"] = "temps"
    handle_update_chart(data)
    
    if dbCount > 100:
        temperature.truncate()
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertVictronVoltage/', methods=['POST'])
def insertVictron(volts=0):
    data = request.json
    print(data)
    dbCount = victron.insert(data[0])

    handle_update_chart(data)
    
    if dbCount > 100:
        victron.truncate()
    
    return jsonify(message="NEW DATA INSERTED", data=data)

@app.route('/insertCurrentShadowBase/', methods=['POST'])
def insertCurrentShadowBase():
    datos = request.json
    print ("CURRENTS: ",datos)
    # data = {
    #     "volts": volts,
    #     "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    # }
    # dbCount = victron.insert(data)

    # handle_update_chart(data)
    
    # if dbCount > 100:
    #     victron.truncate()
    
    return jsonify(message="NEW DATA INSERTED", data=datos)

@app.route('/insertTemperatureShadowBase/', methods=['POST'])
def insertTemperatureShadowBase():
    datos = request.json
    print ("TEMPS: ", datos)
    # data = {
    #     "volts": volts,
    #     "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    # }
    # dbCount = victron.insert(data)

    # handle_update_chart(data)
    
    # if dbCount > 100:
    #     victron.truncate()
    
    return jsonify(message="NEW DATA INSERTED", data=datos)

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

socketio.run(app, host='0.0.0.0', port=8000, debug=True, allow_unsafe_werkzeug=True)
#app.run(host='0.0.0.0', port=8000, debug=True)