from typing_extensions import Unpack
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

from pydantic.config import ConfigDict

date_format = '%m %d %Y %H:%I:%S.%f'

class ClientData(BaseModel):
    voltages: list
    temperatures: list
    timestamp: str
    def volt_minmax(self):
        return min(self.voltages), max(self.voltages)
    
    def temp_minmax(self):
        return min(self.temperatures), max(self.temperatures)
    
    def to_csv_line(self)->str:
        """parse the prop values of this model into a csv line
        """
        datetime_str = datetime.fromisoformat(self.timestamp).strftime(date_format)
        volts = ','.join(str(x) for x in self.voltages)
        temps = ','.join(str(x) for x in self.temperatures)
        
        return datetime_str + ',' + volts + ',' + temps + '\n'
    
    def csv_header(self)->str:
        """returns the header for a csv log file of this model
        """
        volt_headers = ','.join(['volt_' + str(i) for i in range(1, len(self.voltages) + 1)])
        temp_headers = ','.join(['temp_' + str(i) for i in range(1, len(self.temperatures) + 1)])
        
        return 'timestamp,' + volt_headers + ',' + temp_headers + '\n'
    
class AggData(BaseModel):
    volt_min: int
    volt_max:int
    temp_min: int
    temp_max: int
    timestamp: str
    
class RegionDataField(BaseModel):
    value: Optional[Any] = None
    src_ip: Optional[str] = None
    timestamp: Optional[str] = None
    
    def to_csv_line(self)->str:
        
        client_datetime_str = datetime.fromisoformat(self.timestamp).strftime(date_format)
        
        return f"{self.value},{self.src_ip},{client_datetime_str}"
    
    def csv_header(self,field_name:str)->str:
        
        return f"{field_name}-value,{field_name}-src_ip,{field_name}-timestamp"
    
    def update(self, value, src_ip:str, timestamp:str):
        self.value = value
        self.src_ip = src_ip
        self.timestamp = timestamp
        
        return self
    
class RegionData(BaseModel):
    volt_min: Optional[RegionDataField] = RegionDataField()
    volt_max: Optional[RegionDataField] = RegionDataField()
    temp_min: Optional[RegionDataField] = RegionDataField()
    temp_max: Optional[RegionDataField] = RegionDataField()
    latest_timestamp: Optional[str] = None
    router_id: str
    router_timestamp: Optional[str] = None
    
    def to_csv_line(self)->str:
        
        return f"{self.volt_min.to_csv_line()},{self.volt_max.to_csv_line()},{self.temp_min.to_csv_line()},{self.temp_max.to_csv_line()},{self.router_id},{self.router_timestamp}\n"
    
    def csv_header(self)->str:
        
        return f"{self.volt_min.csv_header('volt_min')},{self.volt_max.csv_header('volt_max')},{self.temp_min.csv_header('temp_min')},{self.temp_max.csv_header('temp_max')},router_id,router_timestamp\n"
    
    def update(self, src_ip:str, data: AggData):
        """updates data fields according to its rule or if field value is None

        Args:
            src_ip (str): client ip address
            data (AggData): the aggregated data
        """
        update_latest_time = False
        
        if (self.volt_min.value is None) or (data.volt_min <= self.volt_min.value):
            self.volt_min.update(data.volt_min, src_ip,data.timestamp)
            update_latest_time = True
            
        if (self.volt_max.value is None) or (data.volt_max <= self.volt_max.value):
            self.volt_max.update(data.volt_max, src_ip,data.timestamp)
            update_latest_time = True
            
        if (self.temp_min.value is None) or (data.temp_min <= self.temp_min.value):
            self.temp_min.update(data.temp_min, src_ip,data.timestamp)
            update_latest_time = True
            
        if (self.temp_max.value is None) or (data.temp_max <= self.temp_max.value):
            self.temp_max.update(data.temp_max, src_ip,data.timestamp)
            update_latest_time = True
        
        # update the latest timestamp with timestamp of incoming packet if updates happened
        if update_latest_time:
            self.latest_timestamp = data.timestamp
            
        self.router_timestamp = datetime.utcnow().isoformat()
        
        return self