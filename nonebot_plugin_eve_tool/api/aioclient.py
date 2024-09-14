import aiohttp
import httpx
from pydantic import BaseModel
from ..model import plugin_config


class AsyncHttpClient:
    def __init__(self):
        self.proxy = plugin_config.eve_proxy

    async def _request(self, uri, method, params=None):
        async with httpx.AsyncClient(proxies=self.proxy, timeout=120.0) as client:
            if method == "GET":
                response = await client.get(uri)
                return response.json()
            elif method == "POST":
                response = await client.post(uri, json=params)
                return response.json()
            elif method == "PUT":
                response = await client.put(uri, json=params)
                return response.json()
            else:
                raise ValueError(f"Unsupported method: {method}")

    async def get(self, uri):
        return await self._request(uri, "GET")

    async def post(self, uri, params=None):
        return await self._request(uri, "POST", params)

    async def put(self, uri, params=None):
        return await self._request(uri, "PUT", params)


aioClient = AsyncHttpClient()

