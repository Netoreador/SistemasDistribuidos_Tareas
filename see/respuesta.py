from flask import Flask, jsonify, request
import csv
import statistics
import numpy as np
import requests
import time

app = Flask(__name__)

CSV_PATH = '/data/filtro.csv'

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

@app.route('/data', methods=['POST'])
def receive_data():
    # request.get_json() automatically parses the JSON you sent
    dat = request.get_json()
    
    Query=dat.get('Q')
    Zone=dat.get('Z')
    times=time.time()
    times=times+dat.get('time')

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
    print("back to redis")
    requests.post("http://csv-writer:5000/data", json={"Q":Query,"Z":Zone,"R":respone, "Tasa" : "Miss","time":times})
    return jsonify(respone), 200

@app.route('/data2', methods=['POST'])                 #para query 4
def receive_data_2():
    # request.get_json() automatically parses the JSON you sent
    dat = request.get_json()
    
    Query=dat.get('Q')
    Zone=dat.get('Z')
    Zone2=dat.get('Z2')
    llave=list(ZONAS.keys())
    llave_zone=llave[Zone-1]
    llave_zone2=llave[Zone2-1]
    times=time.time()
    times=times+dat.get('time')

    if Query ==4:

        respone=q4_compare(llave_zone,llave_zone2, 0)

    print("back to redis")
    Zones=Zone*10+Zone2
    requests.post("http://csv-writer:5000/data", json={"Q":Query,"Z":Zones,"R":respone, "Tasa" : "Miss","time":times})
    return jsonify(respone), 200

def q1_count ( zone_id , confidence_min =0.0) :
    records = building [ zone_id ] # registros precargados para la zona
    return sum (1 for r in records if r . get('confidence', 0) >= confidence_min) 

def q2_area ( zone_id , confidence_min =0.0) :
    # Using r['area'] and r['confidence']
    areas = [ r['area_in_meters'] for r in building[zone_id] if r['confidence'] >= confidence_min ]
    return { " avg_area " : statistics.mean ( areas ) , " total_area " : sum ( areas ) , " n " : len ( areas ) }

def q3_density ( zone_id , confidence_min =0.0) :
    count = q1_count ( zone_id , confidence_min )
    area_km2 = ZONAS [ zone_id ]['area_max'] # rea precalculada de la bbox
    return count / area_km2

def q4_compare ( zone_a , zone_b , confidence_min =0.0) :
    da = q3_density ( zone_a , confidence_min )
    db = q3_density ( zone_b , confidence_min )
    return { " zone_a " : da , " zone_b " : db , " winner " : zone_a if da > db else zone_b }

def q5_confidence_dist(zone_id, bins=5):
    # 1. Extract the confidence scores from your pre-loaded data
    # Reminder: Use dictionary indexing r['confidence'] instead of r.confidence
    scores = [r['confidence'] for r in building[zone_id]]

    # 2. Use numpy.histogram to calculate the distribution
    # counts: How many items in each bucket
    # edges: The boundaries (e.g., 0.0, 0.2, 0.4...)
    counts, edges = np.histogram(scores, bins=bins, range=(0, 1))
    print(counts)
    print(edges)
    # 3. Format the result as a list of dictionaries
    distribution = []
    print("???")
    for i in range(bins):
        print("wow")
        distribution.append({
            "bucket": i + 1,
            "min": float(edges[i]),      # Conversion to float is better for JSON
            "max": float(edges[i+1]), 
            "count": int(counts[i])      # Conversion to int is better for JSON
        })
        
    return distribution


if __name__ == "__main__":
    # In Docker, you MUST use host='0.0.0.0' to be reachable
    building = cargar_csv()
    app.run(host='0.0.0.0', port=5000)