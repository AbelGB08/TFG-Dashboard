from pysondb import db
from datetime import datetime
import json

ina226db = db.getDb("ina226db.json")
# ina226db.add({
#     "volts": 20,
#     "amps": 4,
#     "pow": 50,
#     "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
# })
filtered = filter(lambda x: "08-04-2023" <= x["date"] <= "12-04-2023" , ina226db.getAll())
print(list(filtered))
# print(ina226db.getByQuery({"volts":20}))