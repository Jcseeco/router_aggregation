import scapy.all as scapy
import re
from shared import ClientData, AggData, RegionData
import requests
import argparse

class ContentStore:
    contents:dict
    bucket_limit:int
    
    def __init__(self, bucket_limit:int = 5) -> None:
        self.contents = {}
        self.bucket_limit = bucket_limit
    
    def push_data(self,src_ip:str, data: AggData):
        # initialize src data list with new data
        if not src_ip in self.contents:
            self.contents[src_ip] = [data]
            return data
            
        # appends data
        self.contents[src_ip].append(data)
        
        # pop the oldest data if exceeds limit
        if self.bucket_exceeds_limit(src_ip):
            self.pop_bucket_data(src_ip)
            
        return data
    
    def init_src(self, src_ip:str):
        if not src_ip in self.contents:
            self.contents[src_ip] = []
            
    def pop_bucket_data(self, src_ip: str) -> AggData or None:
        """pops the first data item from of the src

        Returns:
            AggData or None: returns None if src_ip not in contents or list empty
        """
        if not src_ip in self.contents or not self.contents[src_ip]:
            return None
        
        return self.contents[src_ip].pop(0)
    
    def bucket_exceeds_limit(self, src_ip: str) -> bool:
        if not src_ip in self.contents or not self.contents[src_ip]:
            return False
        
        return len(self.contents[src_ip]) > self.bucket_limit
        
def is_post_request(raw_payload: str)->bool:
    return raw_payload.startswith("POST")

def extract_preprocess_type(raw_headers:str)->str:
    matched = re.search(r'Preprocess: (.+?)\r\n',raw_headers)
    
    if matched:
        return matched.group(1)
    
    return ''

def is_json_payload(raw_payload:str) -> bool:
    return raw_payload.startswith('{')

def minmax(numbers: list):    
    return min(numbers), max(numbers)

def sniffing(interface: str,filter):
    scapy.sniff(filter=filter,store=False,prn=process_packet)
    
def process_packet(packet: scapy.packet.Packet):
    
    if not packet.haslayer(scapy.Raw):
        return
    
    # decode bytes into string
    raw_payload = packet['Raw'].load.decode('utf-8','ignore')
    
    #get source ip
    src_ip = packet["IP"].src
    
    if is_post_request(raw_payload):
        # extract the data preprocess type if payload of this packet is a POST request header
        preprocess_type = extract_preprocess_type(raw_payload)
        
        # store the preprocess type to its source ip on dict if found in header
        if preprocess_type:
            clients[src_ip] = preprocess_type
            # print(preprocess_type)
    
    elif src_ip in clients and is_json_payload(raw_payload):
        try:
            client_data = ClientData.model_validate_json(raw_payload)
        except Exception as e:
            print(e)
            return
        
        agg_data = store_aggregated_data(src_ip,client_data)
        submit_region_data(src_ip, agg_data)
        
def store_aggregated_data(src_ip: str, client_data: ClientData) -> AggData:
    volt_min,volt_max = client_data.volt_minmax()
    temp_min,temp_max = client_data.temp_minmax()
    
    agg_data = AggData.model_validate({
        "volt_min": volt_min,
        "volt_max": volt_max, 
        "temp_min": temp_min, 
        "temp_max": temp_max,
        "timestamp": client_data.timestamp
    })
    
    return store.push_data(src_ip, agg_data)
    
def submit_region_data(src_ip: str, data: AggData):
    region_data.update(src_ip, data)
    
    # if region data has been modified, submit data
    if region_data.modified:
        region_data.modified = False
        print(f"client: {src_ip} triggered region data update, t={region_data.latest_timestamp}")
        try:
            response = requests.post("http://server2:8001/regionData",
                    json=region_data.model_dump())
        except Exception as e:
            print(e)
    

# this block configurates args
parser = argparse.ArgumentParser()
parser.add_argument("-ri", "--router_id",dest='router_id')
parser.add_argument("-fh", "--filter_host",dest='filter_host',default='server1')
parser.add_argument("-fp", "--filter_port",dest='filter_port',default='8000')
args = parser.parse_args()

# initialize app contents
clients = {}
store = ContentStore()
region_data = RegionData(router_id=args.router_id)

filter = f"dst host {args.filter_host} and dst port {args.filter_port}"

print(f"sniffing dst host: {args.filter_host} and dst port: {args.filter_port}")
sniffing(args.iface, filter)