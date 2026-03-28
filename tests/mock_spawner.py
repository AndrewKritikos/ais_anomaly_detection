import asyncio
import time
import json
import os

from models.Ship import ShipHandler
from core.anomaly_detection import watchdog, yellow_watchdog

async def mock_listen_to_api(handler):
    """
    Παράγει εικονικά δεδομένα AIS για να τεστάρουμε τους Watchdogs.
    Στέλνει νέο στίγμα κάθε 5 δευτερόλεπτα.
    """
    print("🛠️ MOCK API Ξεκίνησε! Δημιουργία εικονικού στόλου...")

    # Μια βασική τοποθεσία ΜΕΣΑ στο Bounding Box σου
    base_lat, base_lon = 1.25, 103.75 

    start_time = time.time()

    while True:
        current_time = time.time()
        elapsed = current_time - start_time

        # 🟢 ΠΛΟΙΟ 1: Το "Καλό" Πλοίο
        handler.process_ping({
            'mmsi': "111111111",
            'lat': base_lat, 
            'lon': base_lon,
            'speed': 12.0, 
            'timestamp': current_time
        })

        # 🟡/🔴 ΠΛΟΙΟ 2: Το "Dark Vessel" 
        if elapsed < 15:
            handler.process_ping({
                'mmsi': "222222222",
                'lat': base_lat + 0.1, 
                'lon': base_lon + 0.1,
                'speed': 14.0, 
                'timestamp': current_time
            })
        elif 15 <= elapsed < 20:
            print("👻 MOCK: Το πλοίο 222222222 μόλις ΕΚΛΕΙΣΕ το AIS του!")

        # 🛸 ΠΛΟΙΟ 3: Το "Spoofing" 
        if elapsed < 30:
            handler.process_ping({
                'mmsi': "333333333",
                'lat': base_lat - 0.1, 
                'lon': base_lon - 0.1,
                'speed': 15.0, 
                'timestamp': current_time
            })
        elif 30 <= elapsed < 35:
            print("🛸 MOCK: Το πλοίο 333333333 κάνει SPOOFING (Τηλεμεταφορά)!")
            handler.process_ping({
                'mmsi': "333333333",
                'lat': 40.0, 
                'lon': 20.0, 
                'speed': 15.0, 
                'timestamp': current_time
            })

        await asyncio.sleep(5)


async def export_state_to_json(handler):
    """
    Διαβάζει τον στόλο κάθε 2 δευτερόλεπτα και τον αποθηκεύει σε ένα αρχείο JSON.
    """
    # Το αρχείο θα σωθεί στον κεντρικό φάκελο, μέσα στο 'data'
    os.makedirs("data", exist_ok=True) 
    
    while True:
        try:
            state = {"green_fleet": [], "yellow_fleet": [], "red_fleet": []}
            
            # Φτιάχνουμε μια μικρή συνάρτηση που μετατρέπει το πλοίο σε απλό λεξικό 
            # με ασφάλεια (κάνει το Enum -> String)
            def safe_ship_dict(ship):
                return {
                    "mmsi": ship.mmsi,
                    "lat": ship.lat,
                    "lon": ship.lon,
                    "speed": ship.speed,
                    "status": str(ship.status), # <--- Εδώ λύνεται το πρόβλημα!
                    "timestamp": ship.timestamp
                }
            
            # Γεμίζουμε τις λίστες
            for ship in handler.green_fleet.values():
                state["green_fleet"].append(safe_ship_dict(ship))
            for ship in handler.yellow_fleet.values():
                state["yellow_fleet"].append(safe_ship_dict(ship))
            for ship in handler.red_fleet.values():
                state["red_fleet"].append(safe_ship_dict(ship))
                
            # Γράφουμε το αρχείο
            with open("data/fleet_state.json", "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)
                
        except Exception as e:
            # Αν κάτι σκάσει, τώρα θα το δούμε στο τερματικό!
            print(f"❌ Σφάλμα κατά την εγγραφή JSON: {e}") 
            
        await asyncio.sleep(2)


async def main():
    test_handler = ShipHandler()
    
    # Τρέχουμε ταυτόχρονα το Fake API, τους Watchdogs και τον JSON Exporter!
    print("🚀 Ξεκινάει το τοπικό σύστημα ελέγχου...")
    await asyncio.gather(
        mock_listen_to_api(test_handler),
        watchdog(test_handler),
        yellow_watchdog(test_handler),
        export_state_to_json(test_handler)
    )

if __name__ == "__main__":
    asyncio.run(main())