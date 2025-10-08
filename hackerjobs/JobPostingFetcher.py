import asyncio

import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from hackerjobs.Posting import Posting


class HNStory(BaseModel):
    id: int
    kids: list[int] = Field(default_factory=list)


class HNComment(BaseModel):
    id: int
    text: str
    time: int
    by: str | None = None


class JobPostingFetcher:
    URL = "https://hacker-news.firebaseio.com/v0/item/"

    def __init__(self, posting_id: int) -> None:
        self.posting_id = posting_id
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.session.close()

    async def get_posting(self) -> list[Posting]:
        story = await self._fetch_story(self.posting_id)
        tasks = [self.__process_item(item) for item in story.kids]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

    async def _fetch_story(self, item_id: int) -> HNStory:
        url = f"{self.URL}{item_id}.json"
        async with self.session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return HNStory.model_validate(data)

    async def _fetch_comment(self, item_id: int) -> HNComment:
        url = f"{self.URL}{item_id}.json"
        async with self.session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return HNComment.model_validate(data)

    async def __process_item(self, item_id: int) -> Posting | None:
        try:
            comment = await self._fetch_comment(item_id)
            text = BeautifulSoup(comment.text, "html.parser").get_text(separator="\n")
            return Posting(
                id=str(item_id),
                text=text,
                by=comment.by or "unknown",
                timestamp=comment.time,
            )
        except Exception:
            # Skip items that don't have the expected comment structure
            return None
