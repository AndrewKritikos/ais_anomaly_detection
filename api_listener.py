import asyncio
import websockets
import json
import time
import os
from dotenv import load_dotenv

from structures.AIS_Signal import AIS_Signal
from structures.Ship import ShipHandler
from utils.position_handler import is_near_border

load_dotenv()
API_KEY = os.getenv("AIS_STREAM_API_KEY")
BOX = [[36.50, 23.50], [38.00, 26.00]]

async def listen_to_api(handler):
    if not API_KEY:
        print("ERROR: No API key found, check .env file")
        return

    master_handler = handler
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


                
async def watchdog(handler):
    """
    Checks for anomalies, currently checks if a ship ping is not close to its mean ping time 
    If it is not, it investigates the position , if the ship is outside of our cover and exited normaly
    Or if the signal is lost inside the cover area meaning that the ship has spoofed its signal or closed
    the transmitter.
    """
    while True:
        await asyncio.sleep(30)
        current_time = time.time()

        for mmsi, ship in list(handler._fleet.items()):
            time_since_last_ping = current_time - ship.timestamp
            avg_ping = getattr(ship, 'avg_ping_sec', 120)
            if avg_ping is None:
                continue
            max_allowed_delay = max(avg_ping * 10, 180)

            if time_since_last_ping > max_allowed_delay:

                if is_near_border(ship.lat, ship.lon, BOX):
                    print(f'The ship with mmsi {mmsi} exited the watch area normaly')
                    del handler._fleet[mmsi]
                else:
                    print(f"PING ANOMALY DETECTED: Ship with mmsi: {mmsi} missing. Avg ping time: {avg_ping:.1f} and last ping was before {time_since_last_ping:.1f}sec")
                    search_specific_ship(mmsi)
    

def search_specific_ship(mmsi):
    """
    Checks a global region to detect a ships position based on its mmsi
    """
    pass