import math

def calculate_distance_nm(lat1, lon1, lat2, lon2):

    R = 3440.065
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def is_near_border(ship, box, time_elapsed_sec):
    """
    Checks if a ship is near the map limits
    ship: Ship's Class
    box: Map box limits [[min_lat, min_lon], [max_lat, max_lon]]
    time_elapsed_sec: Elapsed time from last ping
    return: True if neae limits, False if in the middle of the map
    """
    min_lat = box[0][0]
    min_lon = box[0][1]
    max_lat = box[1][0]
    max_lon = box[1][1]

    dist_south_nm = calculate_distance_nm(ship.lat, ship.lon, min_lat, ship.lon)
    dist_north_nm = calculate_distance_nm(ship.lat, ship.lon, max_lat, ship.lon)
    dist_west_nm = calculate_distance_nm(ship.lat, ship.lon, ship.lat, min_lon)
    dist_east_nm = calculate_distance_nm(ship.lat, ship.lon, ship.lat, max_lon)

    dist_min_nm = min(dist_south_nm, dist_north_nm, dist_west_nm, dist_east_nm)

    time_hours = time_elapsed_sec / 3600
    max_travel_dist_nm = ship.speed * time_hours
    safety_margin_nm = 1.0

    if dist_min_nm <= (max_travel_dist_nm + safety_margin_nm):
        return True
    
    print(f"Ship with mmsi: {ship.mmsi} was lost {dist_min_nm}nm away from nearest border with speed: {ship.speed}")
    return False

def is_inside_watch_area(ais_message, box):

    lat = ais_message['lat']
    lon = ais_message['lon']

    min_lat, min_lon = box[0]
    max_lat, max_lon = box[1]

    is_lat_inside = min_lat <= lat <= max_lat
    is_lon_inside = min_lon <= lon <= max_lon

    return is_lat_inside and is_lon_inside