import asyncio
import requests
from typing import Dict, Any, List

from src.log import logger


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


async def execute_paginated_request(
    search_params, api, total_limit: int
) -> Dict[str, Any]:
    """
    Execute multiple paginated requests to fetch up to total_limit records.

    Returns:
        Combined response dictionary with all results and updated metadata
    """
    batch_size = 300  # GBIF Limit per request
    # Respect initial offset from search_params, default to 0
    initial_offset = search_params.offset or 0
    offset = initial_offset
    all_results = []
    first_response_metadata = None

    while len(all_results) < total_limit:
        remaining = total_limit - len(all_results)
        this_limit = min(batch_size, remaining)

        paginated_params = search_params.model_copy(
            update={"limit": this_limit, "offset": offset}
        )
        request_url = api.build_occurrence_search_url(paginated_params)
        logger.info(f"Request URL: {request_url}")
        try:
            response = await execute_request(request_url)
        except Exception as e:
            # If this is not the first request and we already have some results,
            # return what we have so far
            if all_results:
                break
            raise e

        if first_response_metadata is None:
            first_response_metadata = {
                "count": response.get("count", 0),
                "endOfRecords": response.get("endOfRecords", False),
                "status_code": response.get("status_code", 200),
            }

        batch_results = response.get("results", [])
        if not batch_results:
            break
        all_results.extend(batch_results)

        if response.get("endOfRecords", False) or len(batch_results) < this_limit:
            break
        offset += this_limit

    combined_response = {
        "offset": initial_offset,
        "limit": total_limit,
        "endOfRecords": len(all_results) < total_limit,
        "count": (
            first_response_metadata.get("count", len(all_results))
            if first_response_metadata
            else len(all_results)
        ),
        "results": all_results,
        "status_code": (
            first_response_metadata.get("status_code", 200)
            if first_response_metadata
            else 200
        ),
        "facets": [],
    }

    return combined_response
