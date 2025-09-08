import asyncio

import aiohttp
from bs4 import BeautifulSoup

from hackerjobs.Posting import Posting


class JobPostingFetcher:
    URL = "https://hacker-news.firebaseio.com/v0/item/"

    def __init__(self, posting_id):
        self.posting_id = posting_id
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.session.close()

    async def get_posting(self) -> list[Posting]:
        posting = await self.__fetch(self.posting_id)
        tasks = [self.__process_item(item) for item in posting["kids"]]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

    async def __fetch(self, item_id: int) -> dict:
        url = f"{self.URL}{item_id}.json"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def __process_item(self, item_id: int) -> Posting | None:
        job = await self.__fetch(item_id)
        if "text" in job and "time" in job:
            text = BeautifulSoup(job["text"], "html.parser").get_text(separator="\n")
            return Posting(
                id=str(item_id),
                text=text,
                by=job.get("by", "unknown"),
                timestamp=job["time"]
            )
        return None
