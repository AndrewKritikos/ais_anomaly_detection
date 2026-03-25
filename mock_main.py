import asyncio
from structures.Ship import ShipHandler
from anomaly_detection import watchdog, yellow_watchdog
from mock_spawner import mock_listen_to_api

async def main():
    test_handler = ShipHandler()
    
    # Τρέχουμε ταυτόχρονα το Fake API και τους 2 Watchdogs σου!
    await asyncio.gather(
        mock_listen_to_api(test_handler),
        watchdog(test_handler),        # Ο Πράσινος Watchdog
        yellow_watchdog(test_handler)  # Ο Κίτρινος Watchdog
    )

if __name__ == "__main__":
    asyncio.run(main())