import websockets
import json
import time
import os
from dotenv import load_dotenv



load_dotenv()
API_KEY = os.getenv("AIS_STREAM_API_KEY")
BOX = [[1.00, 103.00], [1.50, 104.50]]

async def listen_to_api(handler):
    if not API_KEY:
        print("ERROR: No API key found, check .env file")
        return

    master_handler = handler
    uri = "wss://stream.aisstream.io/v0/stream"

    async with websockets.connect(uri) as websocket:
        subscribe_message = {
            "APIKey": API_KEY,
            "BoundingBoxes": [BOX],
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


                

    
import asyncio
import time

async def search_specific_ship(mmsi):
    """
    ΠΡΟΣΩΡΙΝΗ MOCK ΣΥΝΑΡΤΗΣΗ: Υποκρίνεται ότι ψάχνει στο παγκόσμιο API.
    """
    print(f"🌍 API SEARCH: Αναζήτηση του πλοίου {mmsi} παγκοσμίως...")
    await asyncio.sleep(1) # Κάνουμε μια μικρή παύση για ρεαλισμό (προσομοίωση δικτύου)

    # Αν ψάχνει το πλοίο 333333333 (Το Spoofing του test μας)
    if mmsi == "333333333":
        # Επιστρέφει ένα στίγμα εκτός του Bounding Box της Σιγκαπούρης!
        return {
            'mmsi': mmsi,
            'lat': 40.0, 
            'lon': 20.0,
            'speed': 15.0,
            'timestamp': time.time()
        }
    
    # Αν ψάχνει το πλοίο 222222222 (Το Dark Vessel του test μας)
    if mmsi == "222222222":
        # Επιστρέφει None, που σημαίνει ότι όντως έχει κλείσει το AIS του παντού!
        return None
        
    return None
