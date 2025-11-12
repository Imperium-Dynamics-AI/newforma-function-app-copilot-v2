"""
GraphClient - HTTP client for Microsoft Graph API.

This module provides a wrapper around aiohttp for making authenticated requests
to the Microsoft Graph API using OAuth 2.0 bearer tokens.
"""

import aiohttp
from src.config.settings import settings


class GraphClient:
    """
    HTTP client for making authenticated requests to Microsoft Graph API.

    Handles authentication token retrieval and request execution with proper
    error handling and response parsing.
    """

    def __init__(self, auth_manager):
        """
        Initialize the GraphClient with an AuthManager instance.

        The AuthManager is responsible for obtaining and refreshing OAuth 2.0
        bearer tokens for authenticating Graph API requests.

        Args:
            auth_manager: The authentication manager for token retrieval.
        """
        self.auth_manager = auth_manager

    async def request(self, method: str, endpoint: str, json_body=None):
        """
        Execute an HTTP request to the Microsoft Graph API.

        Automatically adds authentication headers and constructs the full URL
        from the configured Graph API base URL and the provided endpoint.

        Args:
            method (str): The HTTP method (GET, POST, PUT, DELETE, etc.).
            endpoint (str): The Graph API endpoint path (e.g., "/users/{id}/todo/lists").
            json_body (dict, optional): JSON body for POST/PUT requests. Defaults to None.

        Returns:
            dict: The parsed JSON response from the Graph API, or None for 204 No Content.

        Raises:
            RuntimeError: If the response status code is 400 or higher.
        """
        token = await self.auth_manager.get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"{settings.graph_api_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=json_body) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise RuntimeError(f"Graph API error {resp.status}: {text}")
                # Handle 204 No Content responses (from DELETE operations)
                if resp.status == 204:
                    return None
                return await resp.json()

    async def get(self, endpoint: str):
        """
        Execute a GET request to the Microsoft Graph API.

        Args:
            endpoint (str): The Graph API endpoint path.

        Returns:
            dict: The parsed JSON response from the Graph API.

        Raises:
            RuntimeError: If the response status code is 400 or higher.
        """
        return await self.request("GET", endpoint)

    async def post(self, endpoint: str, json_body=None):
        """
        Execute a POST request to the Microsoft Graph API.

        Args:
            endpoint (str): The Graph API endpoint path.
            json_body (dict, optional): JSON body for the POST request. Defaults to None.

        Returns:
            dict: The parsed JSON response from the Graph API.

        Raises:
            RuntimeError: If the response status code is 400 or higher.
        """
        return await self.request("POST", endpoint, json_body)
