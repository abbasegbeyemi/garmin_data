import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import Any, Callable

from dotenv import load_dotenv
from fastmcp import FastMCP

from garmin import APIClient, AuthClient

load_dotenv()


_garmin_auth_client: AuthClient | None = None
_garmin_api_client: APIClient | None = None
_executor = ThreadPoolExecutor(max_workers=1)

mcp = FastMCP("Garmin Health Agent")


async def run_blocking_call(func: Callable, *args, **kwargs) -> Any:
    """Run a blocking function in a thread pool"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_executor, lambda: func(*args, **kwargs))


@mcp.tool()
async def get_sleep_data(date_start: date, lookback_days: int = 7) -> list[dict]:
    """Get sleep data for the last n days"""
    if _garmin_api_client is None:
        raise Exception("Garmin API client not initialized. Server not logged in.")

    sleep_data = await run_blocking_call(
        _garmin_api_client.get_sleep_data,
        date_start=date_start,
        lookback_days=lookback_days,
    )
    return sleep_data


@mcp.tool()
async def ping() -> str:
    return "pong"


async def initialise_garmin_client():
    """Initialise the Garmin client"""
    global _garmin_auth_client, _garmin_api_client

    _garmin_auth_client = AuthClient()

    if not _garmin_auth_client.is_logged_in():
        raise Exception("Garmin client not logged in. Perform a manual log in.")

    _garmin_api_client = APIClient(_garmin_auth_client)


async def main():
    """Main function to run the server"""
    await initialise_garmin_client()
    if os.getenv("ENVIRONMENT") == "development":
        await mcp.run_async()
    else:
        await mcp.run_async("http", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    asyncio.run(main())
