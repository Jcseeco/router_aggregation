import requests
import random
from datetime import datetime
import time
import argparse

def measure()->dict:
    return {
        "voltages": [random.randint(3400, 3450) for _ in range(10)],
        "temperatures": [random.randint(250, 280) for _ in range(5)],
        "timestamp": datetime.utcnow().isoformat()
    }
        

def submit(url: str, data):
    try:
        response = requests.post(url,json=data,headers=headers)
        print(response)
    except requests.RequestException as e:
        print(e)
        
def define_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-dst",dest="dst_url",default="http://hooke:8000",
                        help="destination full url")
    parser.add_argument("-t",dest="interval",default=1,
                        type=int,
                        help="interval in seconds")
    parser.add_argument("-l",dest="limit",default=60,
                        type=int,
                        help="limit of requests sent")
    
    return parser

def main():
    parser = define_args()
    args = parser.parse_args()
    
    count = 0
    while True:
        count +=1
        if count > args.limit:
            break
        
        submit(args.dst_url,measure())
        time.sleep(args.interval)
        

headers ={
    "Content-Type":"application/json",
    "Preprocess":"minmax"
}

main()