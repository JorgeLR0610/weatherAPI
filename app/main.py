from fastapi import FastAPI
import api.vscrossingClient

app = FastAPI()

@app.get("/weather")
async def get_weather(address: str):
    return await api.vscrossingClient.fetch_vscrossing(address)