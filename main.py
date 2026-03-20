import asyncio
from api_listener import listen_to_api, watchdog
from structures.Ship import ShipHandler


async def main():
    master_handler = ShipHandler()
    api_task = asyncio.create_task(listen_to_api(master_handler))
    watchdog_task = asyncio.create_task(watchdog(master_handler))

    await asyncio.gather(api_task, watchdog_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interupted by User")
