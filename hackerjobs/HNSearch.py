import aiohttp


async def get_latest_hiring_post_id() -> int:
    """Search Algolia HN API for the latest 'Who is hiring' post.

    Returns the HN item ID of the most recent "Ask HN: Who is hiring?" thread.
    """
    url = "https://hn.algolia.com/api/v1/search_by_date"
    params = "query=Ask%20HN%3A%20Who%20is%20hiring%3F&tags=story,author_whoishiring&hitsPerPage=1"

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}?{params}") as response:
            response.raise_for_status()
            data = await response.json()

    hits = data.get("hits", [])
    if not hits:
        raise ValueError("No 'Who is hiring' posts found")

    return int(hits[0]["objectID"])
