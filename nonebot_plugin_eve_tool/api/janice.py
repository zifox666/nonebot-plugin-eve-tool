import httpx

from ..model import plugin_config


class Appraisal:
    def __init__(self, contract: str, persist: bool = False):
        self.contract: str = contract
        self.code: str = ""
        self.totalVolume: int = 0
        self.totalBuyPrice: int = 0
        self.totalSplitPrice: int = 0
        self.totalSellPrice: int = 0
        self.janiceUrl: str = ""

        self.url: str = (
            f"https://janice.e-351.com/api/rest/v1/appraisal?"
            f"key={plugin_config.eve_janice_api_key}&persist={persist}"
        )
        self.headers: dict = {
            'User-Agent': 'NoneBot/2.4.1',
            'Content-Type': 'text/plain',
            'Accept': '*/*',
            'Host': 'janice.e-351.com',
            'Connection': 'keep-alive'
        }

    async def load_data(self):
        data = await self._request()
        self.code = data.get('code', 0)
        self.totalSplitPrice = data['totalSplitPrice']
        self.totalBuyPrice = data['totalBuyPrice']
        self.totalSellPrice = data['totalSellPrice']
        self.totalVolume = data['totalVolume']
        self.janiceUrl: str = f"https://janice.e-351.com/a/{self.code}"

    async def _request(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, headers=self.headers, data=self.contract.encode('utf-8'))
            response.raise_for_status()
            return response.json()
