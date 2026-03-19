from dataclasses import dataclass

@dataclass
class AIS_Signal:
    mmsi: str
    lat: float
    lon: float
    speed: float
    timestamp: float