import httpx

BASE = "https://api.short.io"


async def fetch_domains(api_key: str) -> list[dict]:
    """Return list of domain dicts from a Short.io account."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE}/api/domains",
            headers={"Authorization": api_key, "Accept": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


async def fetch_links(api_key: str, shortio_domain_id: int) -> list[dict]:
    """Fetch all links for a domain from Short.io, handling pagination."""
    links = []
    params = {"domain_id": shortio_domain_id, "limit": 150}
    async with httpx.AsyncClient() as client:
        while True:
            resp = await client.get(
                f"{BASE}/api/links",
                headers={"Authorization": api_key},
                params=params,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            batch = data.get("links", [])
            links.extend(batch)
            if len(batch) < 150:
                break
            params["before"] = batch[-1]["idString"]
    return links


async def create_link(
    api_key: str,
    hostname: str,
    original_url: str,
    slug: str,
    title: str = None,
) -> dict:
    """
    Create a short link. Returns the full response dict on success.
    Raises httpx.HTTPStatusError on failure — caller should catch and
    surface resp.text to the user.
    """
    payload = {
        "domain": hostname,
        "originalURL": original_url,
        "path": slug,
        "allowDuplicates": False,
    }
    if title:
        payload["title"] = title

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE}/links",
            json=payload,
            headers={"Authorization": api_key, "Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
