import httpx


async def lookup_podcast(apple_id: str) -> dict | None:
    """
    Look up a podcast via the iTunes API.
    Returns the result dict (includes feedUrl) or None if not found.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://itunes.apple.com/lookup",
            params={"id": apple_id, "entity": "podcast"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

    if data.get("resultCount", 0) == 0:
        return None
    return data["results"][0]
