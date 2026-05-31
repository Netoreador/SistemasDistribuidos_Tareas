import time
import json
import random
import requests
#from flask import request, Flask, jsonify
from confluent_kafka import Producer

prod = Producer({'bootstrap.servers': 'kafka:29092'})

def ejecutar_consultas():
    hits = 0
    misses = 0

    Query = random.randrange(1,6)
    Zone = random.randrange(1,6)
    

    print("sending ", Query, " ", Zone)
    if Query == 4:
        Zone2 = random.randrange(1,5)
        data = {"Q":Query, "Z":Zone, "Z2": Zone2, "T":time.time()}
        response = prod.produce('queries', value=json.dumps(data).encode('utf-8'))

    else:
        data = {"Q":Query, "Z":Zone,  "T":time.time()}
        response = prod.produce('queries', value=json.dumps(data).encode('utf-8'))

def ejecutar_consultas_zipf():
    
    val_zone=[1,2,3,4,5]
    zipf_zone=[1/1,1/2,1/3,1/4,1/5]

    val_query=[1,2,3,4,5]
    zipf_query=[1/1,1/2,1/3,1/4,1/5]

    Query = random.choices(val_query,weights=zipf_query)[0]
    Zone = random.choices(val_zone,weights=zipf_zone)[0]
    print("sending ", Query, " ", Zone)
    if Query == 4:
        Zone2 = random.randrange(1,5)
        data = {"Q":Query, "Z":Zone, "Z2": Zone2, "T":time.time()}
        prod.produce('queries2', value=json.dumps(data).encode('utf-8'))

    else:

        data = {"Q":Query, "Z":Zone,  "T":time.time()}
        prod.produce('queries', value=json.dumps(data).encode('utf-8'))


if __name__ == '__main__':
    print("start")
    #x=input("Apretar 1 para distribucion normal, 2 para zipf")
    'Para distribucion normal x=1, para zipf x=2'
    x = 1    
    if x == 1:
        while True:
            try:
                ejecutar_consultas()
                prod.poll(0)
                time.sleep(1)
            except:
                print("Nope")
                time.sleep(5)
    elif x == 2:
        while True:
            try:
                ejecutar_consultas_zipf()
                prod.poll(0)
                time.sleep(1)
            except:
                print("Nope")
                time.sleep(5)
