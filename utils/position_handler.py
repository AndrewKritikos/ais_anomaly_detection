
def is_near_border(lat, lon, box, tolerance=0.02):
    """
    Checks if a ship is near the map limits
    lat: Current ships latitude
    lon: Current ships longitude
    box: Map box limits [[min_lat, min_lon], [max_lat, max_lon]]
    tolerance: distance from limit in deg (0.02 = 1.2 nm)
    return: True if neae limits, False if in the middle of the map
    """
    min_lat = box[0][0]
    min_lon = box[0][1]
    max_lat = box[1][0]
    max_lon = box[1][1]

    near_south = abs(lat - min_lat) <= tolerance
    near_north = abs(lat - max_lat) <= tolerance
    near_west = abs(lat - min_lon) <= tolerance
    near_east = abs(lat - max_lon) <= tolerance

    if near_south or near_north or near_west or near_east:
        return True
    
    return False