import time
import json
import random
import requests
from flask import request, Flask, jsonify

times = time.time()

def ejecutar_consultas():
    hits = 0
    misses = 0

    Query = random.randrange(1,6)
    Zone = random.randrange(1,5)
    print("sending ", Query, " ", Zone)
    if Query == 4:
        Zone2 = random.randrange(1,5)
        response = requests.post("http://redis-manager:5000/data2", json={"Q":Query,"Z":Zone,"Z2":Zone2,"time":times})

    else:

        response = requests.post("http://redis-manager:5000/data", json={"Q":Query,"Z":Zone,"time":times})

def ejecutar_consultas_zipf():
    
    val_zone=[1,2,3,4,5]
    zipf_zone=[1/1,1/2,1/3,1/4,1/5]

    val_query=[1,2,3,4,5,6]
    zipf_query=[1/1,1/2,1/3,1/4,1/5,1/6]

    Query = random.choices(val_query,weights=zipf_query)
    Zone = random.choices(val_zone,weights=zipf_zone)
    print("sending ", Query, " ", Zone)
    if Query == 4:
        Zone2 = random.randrange(1,5)
        response = requests.post("http://redis-manager:5000/data2", json={"Q":Query,"Z":Zone,"Z2":Zone2,"time":times})

    else:

        response = requests.post("http://redis-manager:5000/data", json={"Q":Query,"Z":Zone,"time":times})


if __name__ == '__main__':
    print("start")
    #x=input("Apretar 1 para distribucion normal, 2 para zipf")
    'Para distribucion normal x=1, para zipf x=2'
    x = 1    
    if x == 1:
        while True:
            try:
                ejecutar_consultas()
                time.sleep(1)
            except:
                print("Nope")
                time.sleep(5)
    elif x == 2:
        while True:
            try:
                ejecutar_consultas_zipf()
                time.sleep(1)
            except:
                print("Nope")
                time.sleep(5)
