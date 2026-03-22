import time
import random
import asyncio
from structures.Ship import ShipHandler

async def run_fuzzer(handler, num_ships=3, duration_seconds=20):
    print("🧪 Ξεκινάει το Data Fuzzing (Προσομοίωση Ροής AIS)...")
    current_time = time.time()

    # ==========================================
    # 🎬 ΚΙΝΗΜΑΤΙΚΟ ΤΕΣΤ ΣΥΝΟΡΩΝ (Kinematic Border Test)
    # Βόρειο σύνορο: lat = 1.50. Τα βάζουμε στο 1.46 (Απόσταση: 2.4 Ναυτικά Μίλια)
    # ==========================================
    print("\n" + "="*50)
    print("🚀 ΣΤΗΣΙΜΟ ΚΙΝΗΜΑΤΙΚΟΥ ΤΕΣΤ ΣΥΝΟΡΩΝ...")
    lat_pos = 1.46
    lon_pos = 103.50
    
    # 1. ΤΟ ΓΡΗΓΟΡΟ (Θα μπορέσει να "αποδράσει" φυσιολογικά)
    handler.process_ping({'mmsi': '888888881', 'lat': lat_pos, 'lon': lon_pos, 'speed': 30.0, 'timestamp': current_time - 210})
    handler.process_ping({'mmsi': '888888881', 'lat': lat_pos, 'lon': lon_pos, 'speed': 30.0, 'timestamp': current_time - 200})
    print("🚢 Προστέθηκε ΓΡΗΓΟΡΟ πλοίο (30 knots) κοντά στα σύνορα.")

    # 2. ΤΟ ΣΤΑΜΑΤΗΜΕΝΟ (Είναι αδύνατον να βγει από τον χάρτη)
    handler.process_ping({'mmsi': '888888882', 'lat': lat_pos, 'lon': lon_pos, 'speed': 0.0, 'timestamp': current_time - 210})
    handler.process_ping({'mmsi': '888888882', 'lat': lat_pos, 'lon': lon_pos, 'speed': 0.0, 'timestamp': current_time - 200})
    print("⚓ Προστέθηκε ΣΤΑΜΑΤΗΜΕΝΟ πλοίο (0 knots) κοντά στα σύνορα.")
    print("="*50 + "\n")

    # ==========================================
    # 🚢 ΤΟ "ΝΕΟ" ΠΛΟΙΟ (Στέλνει μόνο 1 ping)
    # ==========================================
    one_ping_mmsi = "999999999"
    handler.process_ping({
        'mmsi': one_ping_mmsi, 'lat': 1.25, 'lon': 103.75, 'speed': 10.0, 'timestamp': current_time
    })

    # ==========================================
    # 🚢 ΑΡΧΙΚΟΠΟΙΗΣΗ ΤΟΥ ΥΠΟΛΟΙΠΟΥ ΣΤΟΛΟΥ
    # ==========================================
    mock_ships = {}
    ping_counts = {}
    
    for i in range(num_ships):
        mmsi = str(100000000 + i)
        mock_ships[mmsi] = {
            'lat': random.uniform(1.10, 1.40),
            'lon': random.uniform(103.10, 104.40),
            'speed': random.uniform(10.0, 20.0)
        }
        ping_counts[mmsi] = 0

    # ==========================================
    # Η ΛΟΥΠΑ ΠΑΡΑΓΩΓΗΣ ΔΕΔΟΜΕΝΩΝ
    # ==========================================
    for step in range(duration_seconds):
        await asyncio.sleep(1) 
        
        if not mock_ships: break
        
        mmsi = random.choice(list(mock_ships.keys()))
        ship = mock_ships[mmsi]
        
        if ping_counts[mmsi] >= 2 and random.random() < 0.15:
            print(f"\n👻 [GHOST] Το κανονικό πλοίο {mmsi} έκλεισε τον πομπό του!")
            handler._fleet[mmsi].timestamp -= 200 
            del mock_ships[mmsi] 
            continue 
            
        ship['lat'] += random.uniform(-0.001, 0.001)
        ship['lon'] += random.uniform(-0.001, 0.001)
        
        handler.process_ping({
            'mmsi': mmsi, 'lat': ship['lat'], 'lon': ship['lon'], 'speed': ship['speed'], 'timestamp': time.time()
        })
        ping_counts[mmsi] += 1 

    await asyncio.sleep(3)
    print("\n✅ Η προσομοίωση ολοκληρώθηκε.")