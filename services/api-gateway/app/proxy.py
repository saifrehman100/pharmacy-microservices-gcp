"""Proxy utilities for forwarding requests to microservices."""
import httpx
from fastapi import Request, HTTPException, status
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


async def forward_request(
    request: Request,
    service_url: str,
    path: str,
    timeout: float = 30.0
) -> Dict[Any, Any]:
    """
    Forward request to a microservice and return the response.

    Args:
        request: The original FastAPI request
        service_url: Base URL of the target service
        path: Path to forward to (without leading slash)
        timeout: Request timeout in seconds

    Returns:
        JSON response from the service

    Raises:
        HTTPException: If the service is unreachable or returns an error
    """
    # Construct full URL
    url = f"{service_url}/{path}"

    # Get request body if present
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except Exception:
            body = None

    # Get query parameters
    query_params = dict(request.query_params)

    # Prepare headers (exclude host, content-length, content-type and other hop-by-hop headers)
    # Exclude content-length and content-type because httpx will set them when we pass json=body
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in [
            "host", "connection", "keep-alive",
            "proxy-authenticate", "proxy-authorization",
            "te", "trailers", "transfer-encoding", "upgrade",
            "content-length", "content-type"
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=request.method,
                url=url,
                params=query_params,
                json=body,
                headers=headers
            )

            # Return response
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json() if response.text else "Service error"
                )

            return response.json() if response.text else {}

    except httpx.TimeoutException:
        logger.error(f"Timeout forwarding request to {url}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Service timeout: {service_url}"
        )
    except httpx.ConnectError:
        logger.error(f"Connection error forwarding request to {url}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {service_url}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error forwarding request to {url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal gateway error"
        )
