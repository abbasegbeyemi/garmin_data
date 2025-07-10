import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from typing import Any, Callable, Literal

from dotenv import load_dotenv
from fastmcp import FastMCP

from garmin import GarminClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("mcp_garmin.log"),
        # You can optionally add logging.StreamHandler() to also see output in the terminal when run manually
    ],
)

logging.info("Garmin MCP server script started.")


load_dotenv()


_garmin_client: GarminClient | None = None
_executor = ThreadPoolExecutor(max_workers=1)

mcp = FastMCP("Garmin Health Agent")


async def run_blocking_call(func: Callable, *args, **kwargs) -> Any:
    """Run a blocking function in a thread pool"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_executor, lambda: func(*args, **kwargs))


@mcp.tool()
async def get_activities(
    from_date: datetime,
    to_date: datetime,
    activity_type: Literal[
        "running",
        "cycling",
        "swimming",
        "multi_sport",
        "fitness_equipment",
        "hiking",
        "walking",
        "other",
    ] = "running",
) -> list[dict]:
    """Get activities for the given date range and activity type.

    Args:
        from_date: The start date of the activity range.
        to_date: The end date of the activity range.
        activity_type: The type of activity to get. Defaults to "running".
    """
    if _garmin_client is None:
        await initialise_garmin_client()

    if _garmin_client is None:
        raise Exception("Garmin API client not initialized. Server not logged in.")

    activities = _garmin_client.get_activities(from_date, to_date, activity_type)
    return activities


@mcp.tool()
async def ping() -> str:
    return "pong"


async def initialise_garmin_client():
    """Initialise the Garmin client"""
    global _garmin_client

    _garmin_client = GarminClient()
    _garmin_client.login()


async def main():
    """Main function to run the server"""
    try:
        logging.info("Initialising Garmin client")
        await initialise_garmin_client()
        logging.info("Garmin client initialised")
        if os.getenv("ENVIRONMENT") == "development":
            logging.info("Running in development mode with STDIO transport")
            await mcp.run_async()
        else:
            port = int(os.getenv("PORT", 8000))
            logging.info(
                f"Running in production mode with HTTP transport on port {port}"
            )
            await mcp.run_async("http", host="0.0.0.0", port=port)
    except Exception as e:
        logging.error(f"A fatal error occured during startup: {e}")
        raise e
    finally:
        logging.info("Garmin client shut down")


async def run_garmin():
    await initialise_garmin_client()
    assert _garmin_client is not None
    activities = _garmin_client.get_activities(
        datetime(2025, 7, 5), datetime(2025, 7, 9), "running"
    )
    print(activities)


if __name__ == "__main__":
    asyncio.run(main())
