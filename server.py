from fastapi import FastAPI, Request
from shared import ClientData, RegionData
from datetime import datetime
import os.path

app = FastAPI()

@app.get("/")
async def root():
    return {"message":"hello world"}

@app.post("/")
async def read_data(data: ClientData, request: Request):
    latency = datetime.utcnow() - datetime.fromisoformat(data.timestamp)
    print(f"latency: {latency}")
    
    log_client_data(request.client.host, data, latency)
    
    return {"message": "logged"}

@app.post("/regionData")
async def read_aggregated(data: RegionData):
    time_now = datetime.utcnow()
    print(f"latency: {time_now - datetime.fromisoformat(data.latest_timestamp)}")
    
    log_region_data(data, time_now)
    
    return {"message": "Item printed"}

def log_client_data(client_ip, data: ClientData, latency):
    """append client data to csv file of current date

    Args:
        data (ClientData):
    """
    filepath = f"./client_data_{datetime.now().strftime('%m-%d')}.csv"
    
    if not os.path.isfile(filepath):
        f = open(filepath,"a")
        f.write(f"client_ip,latency,{data.csv_header()}")
    else:
        f = open(filepath,"a")
    
    f.write(f"{client_ip},{latency},{data.to_csv_line()}")
    f.close()
    
def log_region_data(data: RegionData, received_time: datetime):
    """append regional data to csv file of current date

    Args:
        data (RegionData)
        received_time (datetime): the time server received the data
    """
    filepath = f"./region_data_{datetime.now().strftime('%m-%d')}.csv"
    
    if not os.path.isfile(filepath):
        f = open(filepath,"a")
        f.write("received timestamp,latency," + data.csv_header())
    else:
        f = open(filepath,"a")
    
    f.write(f"{received_time.strftime('%m %d %Y %H:%I:%S.%f')},{received_time - datetime.fromisoformat(data.latest_timestamp)},{data.to_csv_line()}")
    f.close()