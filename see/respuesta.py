from flask import Flask, jsonify, request
import csv
import statistics
import numpy as np
import requests
import time
from confluent_kafka import Producer, Consumer
import json
import random

app = Flask(__name__)

CSV_PATH = '/data/filtro.csv'

error_count=0

conf = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'backend',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

prod = Producer({'bootstrap.servers': 'kafka:29092'})

# Initialize the consumer
consumer = Consumer(conf)

# 2. Subscribe to the topic(s)
consumer.subscribe(['backend','backend2','retry','retry2'])

# Zonas
ZONAS = {
    'Z1': {'lat_min': -33.445, 'lat_max': -33.420, 'lon_min': -70.640, 'lon_max': -70.600, 'area_max' : 0},
    'Z2': {'lat_min': -33.420, 'lat_max': -33.390, 'lon_min': -70.600, 'lon_max': -70.550, 'area_max' : 0},
    'Z3': {'lat_min': -33.530, 'lat_max': -33.490, 'lon_min': -70.790, 'lon_max': -70.740, 'area_max' : 0},
    'Z4': {'lat_min': -33.460, 'lat_max': -33.430, 'lon_min': -70.670, 'lon_max': -70.630, 'area_max' : 0},
    'Z5': {'lat_min': -33.470, 'lat_max': -33.430, 'lon_min': -70.810, 'lon_max': -70.760, 'area_max' : 0},
}

def cargar_csv():
    edificios = {zona: [] for zona in ZONAS}

    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            zona = fila.get('Zone', '').strip()
            if zona in edificios:
                edificios[zona].append({
                    'latitude': float(fila['latitude']),
                    'longitude': float(fila['longitude']),
                    'area_in_meters': float(fila['area_in_meters']),
                    'confidence': float(fila['confidence']),
                })

    for a in ZONAS:
        ZONAS[a]['area_max'] = (ZONAS[a]['lat_max'] - ZONAS[a]['lat_min'])*(ZONAS[a]['lon_max']-ZONAS[a]['lon_min'])
        
    return edificios

def q1_count ( zone_id , confidence_min =0.0) :
    records = building [ zone_id ]
    return sum (1 for r in records if r . get('confidence', 0) >= confidence_min) 

def q2_area ( zone_id , confidence_min =0.0) :
    areas = [ r['area_in_meters'] for r in building[zone_id] if r['confidence'] >= confidence_min ]
    if len(areas) == 0:
        return { "avg_area": 0, "total_area": 0, "n": 0 }
    return { "avg_area" : statistics.mean ( areas ) , "total_area" : sum ( areas ) , "n" : len ( areas ) }

def q3_density ( zone_id , confidence_min =0.0) :
    count = q1_count ( zone_id , confidence_min )
    area_km2 = ZONAS [ zone_id ]['area_max']
    return count / area_km2

def q4_compare ( zone_a , zone_b , confidence_min =0.0) :
    da = q3_density ( zone_a , confidence_min )
    db = q3_density ( zone_b , confidence_min )
    return { "zone_a" : da , "zone_b" : db , "winner" : zone_a if da > db else zone_b }

def q5_confidence_dist(zone_id, bins=5):
    scores = [r['confidence'] for r in building[zone_id]]
    counts, edges = np.histogram(scores, bins=bins, range=(0, 1))
    print(counts)
    print(edges)
    distribution = []
    print("???")
    for i in range(bins):
        distribution.append({
            "bucket": i + 1,
            "min": float(edges[i]),
            "max": float(edges[i+1]), 
            "count": int(counts[i])
        })
        
    return distribution


if __name__ == "__main__":
    building = cargar_csv()
    print("Backend")
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error(): continue

        data = json.loads(msg.value().decode('utf-8'))
        topic_name = msg.topic()

        try:
            if random.random()<.7:
                raise ConnectionError("error error error test")
            if topic_name=='backend' or topic_name=='retry':
                print("backend1")
                Query=data["Q"]
                Zone=data["Z"]
                times=data["T"]
                ret = data.get("Retry",0)

                llave=list(ZONAS.keys())
                llave_zone=llave[Zone-1]
                if Query==1:
                    respone=q1_count(llave_zone, 0)
                elif Query ==2:
                    respone=q2_area(llave_zone, 0)
                elif Query ==3:
                    respone=q3_density(llave_zone, 0)
                elif Query ==5:
                    respone=q5_confidence_dist(llave_zone)
                else:
                    raise ValueError(f"Unknown query {Query} on backend topic")

                print("back to redis")
                # FIX: produce to respuestas BEFORE committing the kafka message.
                # Previously, if produce() failed after commit(), Redis would never
                # get the result because the original message was already committed
                # and wouldn't be retried.
                respuesta = {"Qr":Query,"Zr":Zone,"R":respone, "T":times}
                prod.produce('respuestas',value=json.dumps(respuesta).encode('utf-8'))
                prod.poll(0)  # flush produce buffer promptly

                requests.post("http://csv-writer:5000/data", json={"Q":Query,"Z":Zone,"R":respone, "Tasa" : "Miss","time":times,"retry":ret})
                consumer.commit(message=msg)  # commit last, only after everything succeeded

            elif topic_name=='backend2' or topic_name=='retry2':
                print("backend2")
            
                Query=data["Q"]
                Zone=data["Z"]
                times=data["T"]
                Zone2=data["Z2"]
                llave=list(ZONAS.keys())
                llave_zone=llave[Zone-1]
                llave_zone2=llave[Zone2-1]
                ret = data.get("Retry",0)

                if Query ==4:
                    respone=q4_compare(llave_zone,llave_zone2, 0)
                else:
                    raise ValueError(f"Unknown query {Query} on backend2 topic")

                print("back to redis2")
                Zones=Zone*10+Zone2

                # FIX: same ordering fix — produce to respuestas2 before committing
                respuesta = {"Qr":Query,"Zr":Zone,"Z2r":Zone2,"R":respone, "T":times}
                prod.produce('respuestas2',value=json.dumps(respuesta).encode('utf-8'))
                prod.poll(0)

                requests.post("http://csv-writer:5000/data", json={"Q":Query,"Z":Zones,"R":respone, "Tasa" : "Miss","time":times,"retry":ret})
                consumer.commit(message=msg)
        
        except Exception as e:
            
            retry = data["Retry"]
            print(f"Exception: {e} — at retrying, retry count={retry}")
            msg_id = data.get("ID", "Unknown")
            q_val = data.get("Q", 0)
            z_val = data.get("Z", 0)

            if retry < 2 :
                data["Retry"] +=1
                if topic_name=='backend' or topic_name=='retry':
                    prod.produce('retry', value=json.dumps(data).encode('utf-8'))
                elif topic_name=='backend2' or topic_name=='retry2':  # FIX: was 'retry' (typo), now 'retry2'
                    prod.produce('retry2',value=json.dumps(data).encode('utf-8'))
                prod.poll(0)
                consumer.commit(message=msg)
            else:
                with open('/data/fails.csv', 'a', newline='') as csvfile:
                    fieldnames = ['ID', 'Query', 'Zone']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if topic_name=='backend' or topic_name=='retry':
                        writer.writerow({'ID':msg_id,'Query': q_val, 'Zone': z_val,})
                    else:
                        z2_val = data.get("Z2", 0)
                        writer.writerow({'ID':msg_id,'Query': q_val, 'Zone': z_val*10+z2_val,})
                consumer.commit(message=msg)  # FIX: was missing — uncommitted retry messages
                                              # would be redelivered on consumer restart
        
        prod.poll(0)
