import asyncio
import requests
from typing import Dict, Any, List


def execute_sync_request(url: str) -> Dict[str, Any]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    result = response.json()
    result["status_code"] = response.status_code
    return result

async def execute_request(url: str) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, execute_sync_request, url)

async def execute_multiple_requests(urls: Dict[str, str]) -> Dict[str, Any]:
    tasks = []
    for endpoint_name, url in urls.items():
        tasks.append(execute_request(url))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    combined_results = {}
    for endpoint_name, result in zip(urls.keys(), results):
        if isinstance(result, Exception):
            combined_results[endpoint_name] = {"error": str(result)}
        else:
            combined_results[endpoint_name] = result

    return combined_results

async def execute_request_with_retry(url: str, max_retries: int = 3) -> Dict[str, Any]:        
    for attempt in range(max_retries + 1):
        try:
            return await execute_request(url)
        except Exception as e:
            if attempt == max_retries:
                raise e
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError("Max retries exceeded")


async def fetch_gbif_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    return await execute_request(url)
