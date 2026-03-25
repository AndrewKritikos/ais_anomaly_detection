import asyncio
import time

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

        # ---------------------------------------------------------
        # 🟢 ΠΛΟΙΟ 1: Το "Καλό" Πλοίο (Μένει πάντα Green)
        # Στέλνει κανονικά pings ασταμάτητα.
        # ---------------------------------------------------------
        handler.process_ping({
            'mmsi': "111111111",
            'lat': base_lat, 
            'lon': base_lon,
            'speed': 12.0, 
            'timestamp': current_time
        })

        # ---------------------------------------------------------
        # 🟡/🔴 ΠΛΟΙΟ 2: Το "Dark Vessel" 
        # Στέλνει σήμα για 15 δευτερόλεπτα, και μετά... "κόβει" το AIS!
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # 🛸 ΠΛΟΙΟ 3: Το "Spoofing" 
        # Ξεκινάει κανονικά, αλλά στο 30ό δευτερόλεπτο τηλεμεταφέρεται εκτός χάρτη!
        # ---------------------------------------------------------
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
                'lat': 40.0, # Βγήκε εκτός χάρτη!
                'lon': 20.0, 
                'speed': 15.0, 
                'timestamp': current_time
            })

        await asyncio.sleep(5) # Περιμένουμε 5 δευτερόλεπτα μέχρι το επόμενο "κύμα" pings