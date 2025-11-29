import httpx
import os
import json
import redis.asyncio as redis
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

# 1. Configurar la conexión (El "Teléfono" rojo hacia Redis)
# decode_responses=True es un truco para que Redis nos devuelva texto en lugar de bytes raros (b'texto').
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def fetch_vscrossing(address: str, api_key = os.getenv("api_key")):
    cache_key = f"weather:{address.lower().strip()}" # Es buena práctica limpiar el input para que "Madrid" y "madrid " sean la misma clave
    
    cached_data = await redis_client.get(cache_key) #Consultar caché
    
    if cached_data: #Si existen datos para esa ciudad en la caché (Redis), devolverlos para no tener que llamar a la API y que sea más rápido
        print("Datos encontrados en caché")
        return json.loads(cached_data)
    
    # Si no estaba en la caché, entonces sí se tiene que llamar a la API
    # Base URL
    base: str = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    
    params: dict = {
        "location": address,
        "key": api_key
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(base, params=params, timeout=30)
            resp.raise_for_status() #Esto lanza excepción si el status no es 200
            data = resp.json()
    
    except httpx.HTTPStatusError as e: #Caso 1: La API respondió pero con código de error 404, 500, etc
        print(f"API error: {e.response.status_code}")
        
        raise HTTPException( #Lanzar error controlado hacia la FastAPI
            status_code=e.response.status_code,
            detail=f"Error fetching forecast: {e.response.text}"
        )
        
    except httpx.RequestError as e: # Caso 2: Error de conexión (Timeout, dns, sin internet)
        print(f"Conection error: {e}")
        
        raise HTTPException(
            status_code=503, # Service unavailable
            detail="It wasn't possible to connect with the external weather service"
        )
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
        
    # Si la data no estaba en la caché, entonces será útil guardarla por si se vuelve a necesitar; json.dumps convierte el diccionario 'data' a un string; ex=3600 es para que Redis olvide eso en una hora (3600s)
    await redis_client.set(cache_key, json.dumps(data), ex=3600)  
    print("Data saved in Redis for one hour")  

    return data  