import time
import asyncio

from utils.position_handler import is_near_border, is_inside_watch_area
from api_listener import search_specific_ship
from structures.Ship import ShipStatus, ShipHandler

BOX = [[1.00, 103.00], [1.50, 104.50]]


def check_if_missing(handler, mmsi, ship, box, current_time):
    """
    Checks if a ship has exited the watch area correctly or if an anomaly is detected
    handler: Ships Handler Class
    mmsi: Ships mmsi
    ship: Ships class
    box: Bounding Box of the search area
    current_time: Time the watchdog has started

    return
    True: If the ship exited the watch area normaly
    False: If there is an anomaly detected
    """
    
    time_since_last_ping = current_time - ship.timestamp
    avg_ping = ship.avg_ping_sec

    if avg_ping is None:
        return False
    
    
    #max_allowed_delay = min(avg_ping * 10, 1850) real delay
    max_allowed_delay = 10 #testing delay time
    if time_since_last_ping > max_allowed_delay:
        if is_near_border(ship, box, time_since_last_ping):
            print(f'The ship with mmsi {mmsi} exited the watch area normaly')
            del handler.green_fleet[mmsi]
            return False
        else:
            print(f"PING ANOMALY DETECTED: Ship with mmsi: {mmsi} missing. Avg ping time: {avg_ping:.1f} and last ping was before {time_since_last_ping:.1f}sec")
            ship.time_entered_yellow = time.time()
            handler.yellow_fleet[mmsi] = ship
            del handler.green_fleet[mmsi]
            return True
        
    return False


async def watchdog(handler):
    """
    Checks for anomalies, currently checks if a ship ping is not close to its mean ping time 
    If it is not, it investigates the position , if the ship is outside of our cover and exited normaly
    Or if the signal is lost inside the cover area meaning that the ship has spoofed its signal or closed
    the transmitter.
    """
    while True:
        await asyncio.sleep(1)
        current_time = time.time()

        for mmsi, ship in list(handler.green_fleet.items()):
            misssing = check_if_missing(handler, mmsi, ship, BOX, current_time)

async def yellow_watchdog(handler):
    while True:
        await asyncio.sleep(10)
        current_time = time.time()

        for mmsi, ship in list(handler.yellow_fleet.items()):
            time_in_yellow = current_time - ship.time_entered_yellow
            if time_in_yellow > 1: #testing value
            #if time_in_yellow > 30: real value
                ship = handler.yellow_fleet.pop(mmsi)
                handler.red_fleet[mmsi] = ship
                print(f'Ship with mmsi: {mmsi} moved to red list due to signal loss, possible AIS shutdown')
                continue
            ais_message = await search_specific_ship(mmsi)
            if ais_message:
                mmsi = ais_message['mmsi']
                lat = ais_message['lat']
                lon = ais_message['lon']
                speed = ais_message['speed']
                timestamp = ais_message['timestamp']
                if not is_inside_watch_area(ais_message, BOX):
                    print(f'Ship with mmsi: {mmsi} detected outside the watch area, gps spoofing detected')
                    ship = handler.yellow_fleet.pop(mmsi)
                    ship.status = ShipStatus.SPOOFING 
                    handler.red_fleet[mmsi] = ship
                else:
                    handler.process_yellow_ship_message(mmsi, lat, lon, speed, timestamp)


                    
