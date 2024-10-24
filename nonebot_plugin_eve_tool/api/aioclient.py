import aiohttp
from pydantic import BaseModel
from ..model import plugin_config


class AsyncHttpClient:
    def __init__(self):
        self.proxy = plugin_config.eve_proxy

    async def _request(self, uri, method, params=None):
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(uri, proxy=self.proxy) as response:
                    return await response.json()
            elif method == "POST":
                async with session.post(uri, json=params, proxy=self.proxy) as response:
                    return await response.json()
            elif method == "PUT":
                async with session.put(uri, json=params, proxy=self.proxy) as response:
                    return await response.json()
            else:
                raise ValueError(f"Unsupported method: {method}")

    async def get(self, uri):
        return await self._request(uri, "GET")

    async def post(self, uri, params=None):
        return await self._request(uri, "POST", params)

    async def put(self, uri, params=None):
        return await self._request(uri, "PUT", params)


aioClient = AsyncHttpClient()

