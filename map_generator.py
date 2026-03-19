import asyncio
import websockets
import json
import folium
from datetime import datetime, timezone

# --- 1. ΟΙ ΠΕΡΙΟΧΕΣ ΜΑΣ ---
HIGH_RISK_ZONES = {
    "1": {"name": "Μαύρη Θάλασσα", "bbox": [[[43.0, 30.0], [46.0, 38.0]]], "center": [44.5, 34.0]},
    "2": {"name": "Ερυθρά Θάλασσα", "bbox": [[[12.0, 42.0], [14.0, 44.0]]], "center": [13.0, 43.0]},
    "3": {"name": "Περσικός Κόλπος", "bbox": [[[24.0, 52.0], [27.0, 57.0]]], "center": [25.5, 54.5]},
    "4": {"name": "Κύπρος / Αν. Μεσόγειος", "bbox": [[[34.0, 32.0], [36.0, 35.0]]], "center": [35.0, 33.5]},
    "5":{"name": "Μάλακκα", "bbox": [[[1.00, 103.00], [1.50, 104.50]]], "center":[37.00, 24.505]}
}

active_ships = {} # Εδώ θα κρατάμε τα πλοία

# --- 2. Η ΣΥΝΑΡΤΗΣΗ ΠΟΥ ΖΩΓΡΑΦΙΖΕΙ ΤΟΝ ΧΑΡΤΗ ---
def update_map(center_coords):
    m = folium.Map(location=center_coords, zoom_start=6, tiles='CartoDB dark_matter')
    
    for mmsi, data in active_ships.items():
        popup_info = f"<b>MMSI:</b> {mmsi}<br><b>Ταχύτητα:</b> {data['sog']} kts"
        folium.CircleMarker(
            location=[data['lat'], data['lon']],
            radius=5, color='cyan', fill=True, fill_color='cyan', fill_opacity=0.8, popup=popup_info
        ).add_to(m)
        
    m.save("live_map.html")
    
    # Προσθήκη Auto-Refresh (κάθε 3 δευτερόλεπτα)
    with open("live_map.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    html_content = html_content.replace('<head>', '<head>\n    <meta http-equiv="refresh" content="3">')
    with open("live_map.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# --- 3. Η ΣΥΝΑΡΤΗΣΗ ΠΟΥ ΤΡΑΒΑΕΙ ΤΑ ΔΕΔΟΜΕΝΑ ---
async def stream_data(api_key, bbox, center_coords):
    subscribe_message = {"APIKey": api_key, "BoundingBoxes": bbox, "FilterMessageTypes": ["PositionReport"]}

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        await websocket.send(json.dumps(subscribe_message))
        print("\n[+] Το ραντάρ συνδέθηκε! Άνοιξε το 'live_map.html' στον Browser σου.")

        # Φτιάχνουμε τον 1ο άδειο χάρτη για να υπάρχει το αρχείο
        update_map(center_coords)

        async for msg_json in websocket:
            msg = json.loads(msg_json)
            if msg.get("MessageType") == "PositionReport":
                ais = msg['Message']['PositionReport']
                mmsi = msg['MetaData']['MMSI']
                
                # Αποθήκευση και ανανέωση χάρτη
                active_ships[mmsi] = {'lat': ais.get('Latitude'), 'lon': ais.get('Longitude'), 'sog': ais.get('Sog', 0)}
                update_map(center_coords)
                
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Νέο στίγμα -> Σύνολο πλοίων: {len(active_ships)}")

# --- 4. ΕΚΤΕΛΕΣΗ ΤΟΥ ΠΡΟΓΡΑΜΜΑΤΟΣ ---
print("="*40 + "\nΣΥΣΤΗΜΑ ΠΑΡΑΚΟΛΟΥΘΗΣΗΣ ΠΛΟΙΩΝ\n" + "="*40)
for key, zone in HIGH_RISK_ZONES.items():
    print(f"[{key}] {zone['name']}")

choice = input("\nΔιάλεξε περιοχή (1-4): ")

if choice in HIGH_RISK_ZONES:
    my_api_key = "6c830d91a03723065ed301b2d5d04b606774ab50" # Μην ξεχάσεις το κλειδί σου!
    selected = HIGH_RISK_ZONES[choice]
    
    print(f"Εκκίνηση για {selected['name']}...")
    asyncio.run(stream_data(my_api_key, selected['bbox'], selected['center']))
else:
    print("Άκυρη επιλογή. Τέλος.")