from flask import Flask, jsonify, request
import csv
import time

app = Flask(__name__)

tiempo_total=time.time()
Total = 0

Hits=0

@app.route('/data', methods=['POST'])
def receive_data():
    global Total
    global Hits
    data = request.get_json()
    
    Q=data.get('Q')
    Z=data.get('Z')
    R=data.get('R')
    R=str(R)
    R=R.strip('\n')
    Res=data.get('Tasa')
    times=data.get('time')
    times = time.time()-times
    retrys=data.get('retry')
    tiempo_elapsado = time.time()-tiempo_total
    if times == 0.0:
        times = 0.01  # FIX: was 'times == 0.01' (comparison instead of assignment)
    if Res == 'Miss':
        Total +=1

    else:
        Total +=1
        Hits += 1

    Ratio = Hits/Total
    print("about to write")
    with open('/data/results.csv', 'a', newline='') as csvfile:
        fieldnames = ['Query', 'Zone', 'Response','#Retry', 'Tasa', 'Ratio','Latency','Throughput']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print("writing")
        
        through = Total/tiempo_elapsado
        writer.writerow({'Query': Q, 'Zone': Z, 'Response' : R,'#Retry':retrys, 'Tasa' : Res, 'Ratio' : Ratio,'Latency':times,'Throughput':through})
    return jsonify(), 200


    
if __name__ == "__main__":
    with open('/data/results.csv', 'a', newline='') as csvfile:
        fieldnames = ['Query', 'Zone', 'Response','#Retry', 'Tasa', 'Ratio','Latency','Throughput']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    app.run(host='0.0.0.0', port=5000)
