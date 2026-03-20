from structures.AIS_Signal import AIS_Signal
from enum import Enum
import time

class ShipStatus(Enum):
    """ Status based on the ship behaviour"""

    MOVING = 'Moving Normally'
    MOORED = 'Anchored/Moored'
    LOST_SIGNAL = 'Signal Loss'
    DARK_VESSEL = 'Intentionaly Signal Loss'
    SPOOFING = 'Jump Anomaly Detected'

class Ship:
    """Ship attributes"""

    def __init__(self, mmsi, lat, lon, speed, status, timestamp):
        self.mmsi = mmsi
        self.lat = lat
        self.lon = lon
        self.speed = speed
        self.status = status
        self.timestamp = timestamp
        self.history = []
        self.avg_ping_sec = None

class ShipHandler:
    def __init__(self):
        self._fleet = {}
        
    def process_ping(self, ais_message):
        """
        When there is a new ping, it checks if it belongs
        to a ship already known or to a new one and acts acordingly
        """
        mmsi = ais_message['mmsi']
        lat = ais_message['lat']
        lon = ais_message['lon']
        speed = ais_message['speed']
        timestamp = ais_message['timestamp']

        if mmsi not in self._fleet:
            if speed < 0.5:
                status = ShipStatus.MOORED
            else:
                status = ShipStatus.MOVING
            self._fleet[mmsi] = Ship(mmsi, lat, lon, speed, status, timestamp)
            self._fleet[mmsi].history.append({
                'lat': lat,
                'lon': lon,
                'speed': speed,
                'time': timestamp
            })
            print('Ship detected')
        else:
            
            self.update_ship(mmsi, lat, lon, speed, timestamp)

    def update_ship(self, mmsi, new_lat, new_lon, new_speed, new_timestamp):
        """
        Updates the details of a known ship after a ping
        """
        ship = self._fleet[mmsi]
        time_diff = (new_timestamp - ship.timestamp) / 60

        if ship.avg_ping_sec is None: #checking if there is previous avg
            ship.avg_ping_sec = time_diff * 60
        else:
            ship.avg_ping_sec = (0.8 * ship.avg_ping_sec) + (0.2 * (time_diff * 60)) #calcs new avg

        new_status = ShipStatus.MOORED if new_speed < 0.5 else ShipStatus.MOVING

        if new_status != ShipStatus.MOORED or time_diff >= 10.0:
            if time_diff >= 2.0 or ship.status != new_status:
                ship.history.append({
                    'lat': new_lat,
                    'lon': new_lon,
                    'speed': new_speed,
                    'time': new_timestamp
                })
                print("updating ship")
        
        ship.lat = new_lat
        ship.lon = new_lon
        ship.speed = new_speed
        ship.timestamp = new_timestamp
        ship.status = new_status