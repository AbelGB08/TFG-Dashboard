from flask import Flask
from flask import request
from pysondb import db
from datetime import datetime

ina226db = db.getDb("ina226db.json")
app = Flask(__name__)

@app.route('/')
def index():
    # TODO render html view
    return "HELLO WORLD"

@app.route('/getData/<startDate>/<endDate>')
def getData(startDate='a', endDate='b'):
    results = ina226db.getAll()

    filteredResults = []
    for result in results:
        if startDate <= result["date"] <= endDate:
            filteredResults.append(result)

    return filteredResults

@app.route('/insertData/<volts>/<amps>/<pow>')
def insertData(volts=0, amps=0, pow=0):
    ina226db.add({
        "volts": volts,
        "amps": amps,
        "pow": pow,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })
    return "NEW DATA INSERTED"

app.run(port=8000, debug=True)