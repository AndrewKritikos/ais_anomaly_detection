from structures.AIS_Signal import AIS_Signal
from enum import Enum
import time
from utils.position_handler import is_inside_watch_area
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
        self.time_entered_yellow = None

class ShipHandler:
    def __init__(self):
        self.green_fleet = {}
        self.yellow_fleet = {}
        self.red_fleet = {}
        self.ships = 0
        
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

        if mmsi in self.red_fleet:
            self.process_red_ship_message(mmsi, lat, lon, speed, timestamp)
            return
        
        if mmsi in self.yellow_fleet:
            self.process_yellow_ship_message(mmsi, lat, lon, speed, timestamp)
            return
        
        if mmsi not in self.green_fleet:
            self.process_new_ship_message(mmsi, lat, lon, speed, timestamp)

        else:
            self.process_green_ship(mmsi, lat, lon, speed, timestamp)

    def process_new_ship_message(self, mmsi, lat, lon, speed, timestamp):
        if speed < 0.5:
            status = ShipStatus.MOORED
        else:
            status = ShipStatus.MOVING
        self.green_fleet[mmsi] = Ship(mmsi, lat, lon, speed, status, timestamp)
        self.green_fleet[mmsi].history.append({
            'lat': lat,
            'lon': lon,
            'speed': speed,
            'time': timestamp
        })
        print('Ship detected')
        self.ships += 1
        print(f'{self.ships} unique ships loaded')
    
    def process_green_ship(self, mmsi, new_lat, new_lon, new_speed, new_timestamp, was_yellow=False):
        """
        Updates the details of a known ship after a ping
        """
        ship = self.green_fleet[mmsi]
        time_diff_sec = new_timestamp - ship.timestamp
        time_diff_min = time_diff_sec * 60

        if not was_yellow:
            if ship.avg_ping_sec is None: #checking if there is previous avg
                ship.avg_ping_sec = time_diff_sec
            else:
                ship.avg_ping_sec = (0.8 * ship.avg_ping_sec) + (0.2 * (time_diff_sec)) #calcs new avg

        new_status = ShipStatus.MOORED if new_speed < 0.5 else ShipStatus.MOVING

        if new_status != ShipStatus.MOORED or time_diff_min >= 10.0:
            if time_diff_min >= 2.0 or ship.status != new_status:
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

    def process_yellow_ship_message(self, mmsi, lat, lon, speed, timestamp):
        """
        When a ship from yellow list ping again, moves back to green list
        """
        ship = self.yellow_fleet.pop(mmsi)
        ship.time_entered_yellow = None
        self.green_fleet[mmsi] = ship
        print(f'Signal Recovered: Ship with mmsi: {mmsi} pinged again and moved back to green fleet')
        self.process_green_ship(mmsi, lat, lon, speed, timestamp, was_yellow=True)

    def process_red_ship_message(self, mmsi, lat, lon, speed, timestamp):
        pass

    