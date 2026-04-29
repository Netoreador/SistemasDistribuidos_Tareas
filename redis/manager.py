from flask import request, Flask, jsonify 
import redis
import requests
import time

r = redis.Redis(host='redis-db', port=6379, decode_responses=True)
app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json() #automatically parses the JSON you sent
   # data = request.get_json
    print("At recieve")
    Q=data.get('Q')
    Z=data.get('Z')
    Sums=Q*10+Z
    times=time.time()
    times=times+data.get('time')

    Q1=data.get('Q1')
    Z1=data.get('Z1')

    check=r.exists(str(Sums))
    print("Check: ", check)
    if check == 0:   #send to respuesta
        print("send to backend")
        response = requests.post("http://node-app:5000/data", json={"Q":Q,"Z":Z,"time":times})
        print(response.json())
        r.set(str(Sums),response.text, ex=100)
        print("at 0")
        print(r.get(str(Sums)))
        return jsonify(response.json()), 200
    else:
        cache_response = r.get(str(Sums))
        print("at 1")
        requests.post("http://csv-writer:5000/data", json={"Q":Q,"Z":Z,"R":cache_response, "Tasa" : "Hit","time":times})
        return jsonify({"data" : cache_response}), 200
    
@app.route('/data2', methods=['POST'])
def receive_data_2():
    data = request.get_json() #automatically parses the JSON you sent
   # data = request.get_json
    print("At recieve")
    Q=data.get('Q')
    Z=data.get('Z')
    Z2=data.get('Z2')
    Sums=Q*100+Z*10+Z2
    times=time.time()
    times=times+data.get('time')

    Q1=data.get('Q1')
    Z1=data.get('Z1')

    check=r.exists(str(Sums))
    print("Check: ", check)
    if check == 0:   #send to respuesta
        print("send to backend")
        response = requests.post("http://node-app:5000/data2", json={"Q":Q,"Z":Z,"Z2":Z2,"time":times})
        print(response.json())
        r.set(str(Sums),response.text, ex=100)
        print("at 0")
        print(r.get(str(Sums)))
        return jsonify(response.json()), 200
    else:
        cache_response = r.get(str(Sums))
        Zones=Z*10+Z2
        print("at 1")
        requests.post("http://csv-writer:5000/data", json={"Q":Q,"Z":Zones,"R":cache_response, "Tasa" : "Hit","time":times})
        return jsonify({"data" : cache_response}), 200

if __name__ == "__main__":
    # In Docker, you MUST use host='0.0.0.0' to be reachable
    print("manager runin")
    app.run(host='0.0.0.0', port=5000)