from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Data(BaseModel):
    voltages: list
    temperatures: list
    timestamp: str

@app.get("/")
async def root():
    return {"message":"hello world"}

@app.post("/")
async def read_data(data: Data):
    print(data)
    return {"message": "Item printed"}