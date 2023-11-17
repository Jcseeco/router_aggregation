from pydantic import BaseModel

class ClientData(BaseModel):
    voltages: list
    temperatures: list
    timestamp: str
    def volt_minmax(self):
        return min(self.voltages), max(self.voltages)
    
    def temp_minmax(self):
        return min(self.temperatures), max(self.temperatures)
    
class AggData(BaseModel):
    volt_min: int
    volt_max:int
    temp_min: int
    temp_max: int
    timestamp: str
    
class TracedData(BaseModel):
    volt_min: int
    volt_max:int
    temp_min: int
    temp_max: int
    timestamp: str
    src_ip: str
    router_id: str
    router_timestamp: str