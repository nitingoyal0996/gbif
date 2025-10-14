import asyncio
import requests
from typing import Dict, Any

from src.log import logger
from ichatbio.agent_response import IChatBioAgentProcess


def execute_sync_request(url: str, max_retries: int = 3) -> Dict[str, Any]:
    """Execute a sync request with retry logic for 500 status codes."""
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, timeout=30)

            if response.status_code >= 500:
                if attempt < max_retries:
                    logger.warning(
                        f"Got {response.status_code} status, retrying (attempt {attempt + 1}/{max_retries})"
                    )
                    continue
                else:
                    response.raise_for_status()

            response.raise_for_status()
            result = response.json()
            result["status_code"] = response.status_code
            return result

        except requests.exceptions.HTTPError as e:
            if attempt == max_retries or (e.response and e.response.status_code < 500):
                raise
            logger.warning(
                f"Request failed: {e}, retrying (attempt {attempt + 1}/{max_retries})"
            )

    raise RuntimeError("Max retries exceeded")


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

async def fetch_gbif_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    return await execute_request(url)


async def execute_paginated_request(
    search_params, api, total_limit: int, process: IChatBioAgentProcess
) -> Dict[str, Any]:
    """
    Execute multiple paginated requests to fetch up to total_limit records.

    Returns:
        Combined response dictionary with all results and updated metadata
    """
    batch_size = 300
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
        await process.log(f"Request URL: {request_url}")
        try:
            response = await execute_request(request_url)
        except Exception as e:
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
