import asyncio
import websockets
import json
import time
import os
from dotenv import load_dotenv

from structures.AIS_Signal import AIS_Signal
from structures.Ship import ShipHandler

load_dotenv()
API_KEY = os.getenv("AIS_STREAM_API_KEY")

async def listen_to_api():
    if not API_KEY:
        print("ERROR: No API key found, check .env file")
        return

    master_handler = ShipHandler()
    uri = "wss://stream.aisstream.io/v0/stream"

    async with websockets.connect(uri) as websocket:
        subscribe_message = {
            "APIKey": API_KEY,
            "BoundingBoxes": [[[36.50, 23.50], [38.00, 26.00]]],
            "FilterMessageTypes": ["PositionReport", "StandardClassBPositionReport"]
        }
    
        await websocket.send(json.dumps(subscribe_message))
        print("API Connected successfully")

        async for mesage_json in websocket:
            data = json.loads(mesage_json)
            msg_type = data["MessageType"]

            if msg_type in ["PositionReport", "StandardClassBPositionReport"]:
                report = data["Message"][msg_type]
                
                ais_message = {
                    'mmsi': str(report["UserID"]),
                    'lat': report["Latitude"],
                    'lon': report["Longitude"],
                    'speed': report["Sog"],
                    'timestamp': time.time()
                }
                
                master_handler.process_ping(ais_message)
                

    

