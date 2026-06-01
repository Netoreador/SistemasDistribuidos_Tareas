from flask import request, Flask, jsonify 
import redis
import requests
import time
from confluent_kafka import Producer, Consumer
import json

r = redis.Redis(host='redis-db', port=6379, decode_responses=True)
app = Flask(__name__)

conf = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'redis',
    'auto.offset.reset': 'earliest'
}

prod = Producer({'bootstrap.servers': 'kafka:29092'})

consumer = Consumer(conf)
consumer.subscribe(['queries','queries2','respuestas','respuestas2'])


if __name__ == "__main__":
    print("manager running")
    
    while True:

        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        try:
            data = json.loads(msg.value().decode('utf-8'))
            topic_name = msg.topic()

            if topic_name == 'queries':
                print("At receive")
                Q=data["Q"]
                Z=data["Z"]
                Sums=Q*10+Z
                times=data["T"]
                retry=data.get("Retry",0)

                check=r.exists(str(Sums))
                print("Check: ", check)
                if check == 0:   #send to respuesta
                    print("send to backend")
                    prod.produce('backend',value=json.dumps(data).encode('utf-8'))
                    
                else:
                    cache_response = r.get(str(Sums))
                    print("at 1")
                    requests.post("http://csv-writer:5000/data", json={"Q":Q,"Z":Z,"R":cache_response, "Tasa" : "Hit","time":times,"retry":retry})
            
            elif topic_name=='queries2':
                print("At receive2")
                Q=data["Q"]
                Z=data["Z"]
                Z2=data["Z2"]
                Sums=Q*100+Z*10+Z2
                times=data["T"]
                retry=data.get("Retry",0)

                check=r.exists(str(Sums))
                print("Check: ", check)
                if check == 0:   #send to respuesta
                    print("send to backend2")
                    prod.produce('backend2',value=json.dumps(data).encode('utf-8'))
                else:
                    cache_response = r.get(str(Sums))
                    Zones=Z*10+Z2
                    print("at 1")
                    requests.post("http://csv-writer:5000/data", json={"Q":Q,"Z":Zones,"R":cache_response, "Tasa" : "Hit","time":times,"retry":retry})

            elif topic_name == 'respuestas':
                print("Respuesta1")
                Q=data["Qr"]
                Z=data["Zr"]
                Sums=Q*10+Z
                Res = data["R"]

                r.set(str(Sums),json.dumps(Res), ex=100)
                print("Stored in Redis:", r.get(str(Sums)))
            
            elif topic_name == 'respuestas2':
                print("Respuesta2")
                Q=data["Qr"]
                Z=data["Zr"]
                Z2=data["Z2r"]
                Sums=Q*100+Z*10+Z2
                Res = data["R"]

                r.set(str(Sums),json.dumps(Res), ex=10)
                print("Stored in Redis:", r.get(str(Sums)))

        except Exception as e:

            print(f"oops")

        prod.poll(0)
