import time

from utils.position_handler import is_near_border
#from api_listener import search_specific_ship


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
    
    
    max_allowed_delay = max(avg_ping * 10, 180)
    
    if time_since_last_ping > max_allowed_delay:
        if is_near_border(ship, box, time_since_last_ping):
            print(f'The ship with mmsi {mmsi} exited the watch area normaly')
            del handler._fleet[mmsi]
            return False
        else:
            print(f"PING ANOMALY DETECTED: Ship with mmsi: {mmsi} missing. Avg ping time: {avg_ping:.1f} and last ping was before {time_since_last_ping:.1f}sec")
            #search_specific_ship(mmsi)
            return True
        
    return False