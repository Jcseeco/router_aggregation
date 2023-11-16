import requests
import random
from datetime import datetime
import time
import json

host = 'http://10.10.2.100:8000'

def measure()->dict:
    return {
        "voltages": [random.randint(3400, 3450) for _ in range(10)],
        "temperatures": [random.randint(250, 280) for _ in range(5)],
        "timestamp": datetime.now().isoformat()
    }
        

def submit(host: str, data):
    try:
        response = requests.post(host,json=data)
        print(response)
    except requests.RequestException as e:
        print(e)
        
def main():
    count = 0
    while True:
        count +=1
        if count > 10:
            break
        # print(json.dumps(measure()))
        submit(host,measure())
        time.sleep(1)
        
main()