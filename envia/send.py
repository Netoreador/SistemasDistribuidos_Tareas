import time
import json
import random
import requests
from flask import request, Flask, jsonify



def ejecutar_consultas():
    hits = 0
    misses = 0

    Query = random.randrange(1,5)
    Zone = random.randrange(1,5)
    print("sending ", Query, " ", Zone)
    if Query == 4:
        Zone2 = random.randrange(1,5)
        response = requests.post("http://redis-manager:5000/data", json={"Q":Query,"Z":Zone,"Z2":Zone2})

    else:

        response = requests.post("http://redis-manager:5000/data", json={"Q":Query,"Z":Zone})




if __name__ == '__main__':
    print("start")
    time.sleep(5)
    while True:
        try:
            ejecutar_consultas()
            time.sleep(5)
        except:
            print("Nope")
            time.sleep(5)
