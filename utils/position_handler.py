
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

    dist_south = abs(ship.lat - min_lat)
    dist_north = abs(ship.lat - max_lat)
    dist_west = abs(ship.lat - min_lon)
    dist_east = abs(ship.lat - max_lon)

    dist_sorted_deg = sorted([dist_south, dist_north, dist_west, dist_east])

    nearest_dist_deg = dist_sorted_deg[0]

    nearest_dist_nm = nearest_dist_deg * 60
    time_hours = time_elapsed_sec / 3600
    max_travel_dist_nm = ship.speed * time_hours
    safety_margin_nm = 1.0

    if nearest_dist_nm <= (max_travel_dist_nm + safety_margin_nm):
        return True
    
    print(f"Ship with mmsi: {ship.mmsi} was lost {nearest_dist_nm}nm away from nearest border with speed: {ship.speed}")
    return False