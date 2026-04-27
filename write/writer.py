from flask import Flask, jsonify, request
import csv

app = Flask(__name__)


Total = 0

Hits=0

@app.route('/data', methods=['POST'])
def receive_data():
    # request.get_json() automatically parses the JSON you sent
    global Total
    global Hits
    data = request.get_json()
    
    Q=data.get('Q')
    Z=data.get('Z')
    R=data.get('R')
    Res=data.get('Tasa')
    if Res == 'Miss':
        Total +=1

    else:
        Total +=1
        Hits += 1

    Ratio = Hits/Total
    print("about to write")
    with open('results.csv', 'a', newline='') as csvfile:
        fieldnames = ['Query', 'Zone', 'Response', 'Tasa', 'Ratio']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        print("writing")
        writer.writeheader()
        writer.writerow({'Query': Q, 'Zone': Z, 'Response' : R, 'Tasa' : Res, 'Ratio' : Ratio})
    return jsonify(), 200


    
if __name__ == "__main__":
    # In Docker, you MUST use host='0.0.0.0' to be reachable
    app.run(host='0.0.0.0', port=5000)