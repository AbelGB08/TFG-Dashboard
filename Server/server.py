from flask import Flask, request, render_template 
from pysondb import db
from datetime import datetime

ina226db = db.getDb("ina226db.json")
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/getData')
def getData(startDate='a', endDate='b'):
    results = ina226db.getAll()
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    filteredResults = []
    for result in results:
        if startDate <= result["date"] <= endDate:
            filteredResults.append(result)

    dates = [row["date"] for row in filteredResults]
    volts = [row["volts"] for row in filteredResults]
    amps = [row["amps"] for row in filteredResults]
    pow = [row["pow"] for row in filteredResults]
    
    return render_template("index.html", dates=dates, volts=volts, amps=amps, pow=pow)

@app.route('/insertData/<volts>/<amps>/<pow>')
def insertData(volts=0, amps=0, pow=0):
    ina226db.add({
        "volts": volts,
        "amps": amps,
        "pow": pow,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })
    
    return "NEW DATA INSERTED"

app.run(host='0.0.0.0', port=8000, debug=True)