from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import api.vscrossingClient

app = FastAPI()

#1. Montar la carpeta "static"
#Esto hace que http://localhost:8000/static/script.js sea accesible
app.mount("/static", StaticFiles(directory="static"), name="static")

#2. Configurar Jinja2
templates = Jinja2Templates(directory="templates")

#--- RUTAS DE API (JSON) ---
@app.get("/weather")
async def get_weather(address: str):
    return await api.vscrossingClient.fetch_vscrossing(address)

#--- RUTAS DE VISTAS (HTML) ---
@app.get("/")
async def read_root(request: Request):
    # Jinja2 siempre necesita recibir el objeto "request"
    return templates.TemplateResponse("index.html", {"request": request})