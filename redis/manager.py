from flask import request, Flask, jsonify 
import redis
import requests
import time
from confluent_kafka import Producer, Consumer
import json

r = redis.Redis(host='redis-db', port=6379, decode_responses=True)
app = Flask(__name__)

# 1. Configuration uses a dictionary of Kafka properties
conf = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'redis',
    'auto.offset.reset': 'earliest' # Start from the beginning if no offset exists
}

prod = Producer({'bootstrap.servers': 'kafka:29092'})

# Initialize the consumer
consumer = Consumer(conf)

# 2. Subscribe to the topic(s)
consumer.subscribe(['queries','queries2','respuestas','respuestas2'])




if __name__ == "__main__":
    # In Docker, you MUST use host='0.0.0.0' to be reachable
    print("manager runin")
    
    while True :

        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error(): continue

        data = json.loads(msg.value().decode('utf-8'))
        topic_name = msg.topic()

        if topic_name == 'queries':
    # data = request.get_json
            print("At recieve")
            Q=data["Q"]
            Z=data["Z"]
            Sums=Q*10+Z
            times=data["T"]

            check=r.exists(str(Sums))
            print("Check: ", check)
            if check == 0:   #send to respuesta
                print("send to backend")
                prod.produce('backend',value=json.dumps(data).encode('utf-8'))
                
            else:
                cache_response = r.get(str(Sums))
                print("at 1")
                requests.post("http://csv-writer:5000/data", json={"Q":Q,"Z":Z,"R":cache_response, "Tasa" : "Hit","time":times})
        
        elif topic_name=='queries2':
            print("At recieve")
            Q=data["Q"]
            Z=["Z"]
            Z2=["Z2"]
            Sums=Q*100+Z*10+Z2
            times=data["T"]

            Q1=data.get('Q1')
            Z1=data.get('Z1')

            check=r.exists(str(Sums))
            print("Check: ", check)
            if check == 0:   #send to respuesta
                print("send to backend")
                prod.produce('backend2',value=json.dumps(data).encode('utf-8'))
            else:
                cache_response = r.get(str(Sums))
                Zones=Z*10+Z2
                print("at 1")
                requests.post("http://csv-writer:5000/data", json={"Q":Q,"Z":Zones,"R":cache_response, "Tasa" : "Hit","time":times})

        elif topic_name == 'respuestas':
            print("Respuesta1")
            Q=data["Qr"]
            Z=data["Zr"]
            Sums=Q*10+Z
            times=data["T"]
            Res = data["R"]

            r.set(str(Sums),Res, ex=100)
            print("at 0")
            print(r.get(str(Sums)))
        
        elif topic_name == 'respuestas2':
            print("Respuesta2")
            Q=data["Qr"]
            Z=data["Zr"]
            Z2=["Z2r"]
            Sums=Q*100+Z*10+Z2
            times=data["T"]
            Res = data["R"]

            r.set(str(Sums),Res, ex=100)
            print("at 0")
            print(r.get(str(Sums)))
