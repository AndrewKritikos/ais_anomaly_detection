from testing import run_fuzzer
import asyncio
from api_listener import watchdog
from structures.Ship import ShipHandler

async def main():
    handler = ShipHandler()
    watchdog_task = asyncio.create_task(watchdog(handler))

    await run_fuzzer(handler=handler, duration_seconds=20)
    watchdog_task.cancel()


asyncio.run(main())