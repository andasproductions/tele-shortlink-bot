from rss import Episode


def build_podlink_url(apple_id: str, episode: Episode) -> str:
    """
    Construct a pod.link episode URL.
    https://pod.link/{apple_id}/episode/{base64_guid}?view=apps&sort=popularity
    """
    return (
        f"https://pod.link/{apple_id}/episode/{episode.guid_b64}"
        "?view=apps&sort=popularity"
    )
