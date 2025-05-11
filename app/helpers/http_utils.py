import asyncio

from app.config import SERVER_BASE_URL
from ..logger_config import *
import requests

def build_url(endpoint: str) -> str:
    """
    Build the URL for the given endpoint.
    :param endpoint:
    :return:
    """
    return f"{SERVER_BASE_URL}/process/{endpoint}/"

async def post_start_process(process_name: str, pipeline_id: str):
    """
    Start a process by sending a POST request to the server.
    :param process_name:
    :param pipeline_id:
    :return:
    """
    url = build_url(process_name)
    logger.info(f"Start_process {url}")
    try:
        response = requests.post(url, json={"pipeline_id": pipeline_id}, timeout=30.0)
        response.raise_for_status()

    except Exception as e:
        logger.error(f"Exception occurred in post_start_process: {e}", exc_info=True)

        raise

def start_process_safe(process_name: str, pipeline_id: str):
    """
    Start a process safely by checking if an event loop is running.
    :param process_name:
    :param pipeline_id:
    :return:
    """
    # Check if there is an active event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    try:
        if loop and loop.is_running():
            # If there's an active event loop, create a task
            loop.create_task(post_start_process(process_name, pipeline_id))
        else:
            # If there's no active event loop, run the coroutine
            asyncio.run(post_start_process(process_name, pipeline_id))
    except Exception as e:
        logger.error(f"Exception occurred in start_process_safe: {e}", exc_info=True)

        raise


