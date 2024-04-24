import requests
import random
from time import sleep

def insertInas():
    url = "http://localhost:5000/insertData/" + str(random.randint(24, 25)) + "/" + str(random.randint(2, 3)) + "/" + str(0) + "/" + "INA1"
    requests.post(url)
    sleep(0.1)
    url = "http://localhost:5000/insertData/" + str(random.randint(24, 25)) + "/" + str(random.randint(2, 3)) + "/" + str(0) + "/" + "INA2"
    requests.post(url)
    sleep(0.1)
    url = "http://localhost:5000/insertData/" + str(random.randint(24, 25)) + "/" + str(random.randint(2, 3)) + "/" + str(0) + "/" + "INA3"
    requests.post(url)
    sleep(0.1)
    url = "http://localhost:5000/insertData/" + str(random.randint(24, 25)) + "/" + str(random.randint(2, 3)) + "/" + str(0) + "/" + "INA4"
    requests.post(url)
    sleep(0.1)
    url = "http://localhost:5000/insertData/" + str(random.randint(24, 25)) + "/" + str(random.randint(2, 3)) + "/" + str(0) + "/" + "INA5"
    requests.post(url)
    sleep(0.1)

def insertTemps():
    temp1 = random.randint(17, 20)
    temp2 = random.randint(10, 12)
    temp3 = random.randint(14, 17)
    temp4 = random.randint(20, 23)    
    url = "http://localhost:5000/insertTemp/" + str(temp1) + "/" + str(temp2) + "/" + str(temp3) + "/" + str(temp4)
    requests.post(url)
    url = "http://localhost:5000/insertTemperatureShadowBase/" + str(temp1) + "/" + str(temp2) + "/" + str(temp3) + "/" + str(temp4)
    requests.post(url)
    sleep(0.1)

def insertCurrShadowBase():
    url = "http://localhost:5000/insertCurrentShadowBase/" + str(random.randint(5, 15)) + "/" + str(random.randint(5, 15) + 2) + "/" + str(random.randint(5, 15) + 4) + "/" + str(random.randint(5, 15) + 6)
    requests.post(url)
    sleep(0.1)
    
while True:
    insertInas()
    insertTemps()
    insertCurrShadowBase()
    sleep(1)