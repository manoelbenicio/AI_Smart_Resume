"""URL parser — extract Job Description text from a URL."""

from __future__ import annotations

import httpx
from bs4 import BeautifulSoup


def parse_url(url: str) -> str:
    """Fetch a URL and extract the main text content.

    Args:
        url: Full URL to a job description page.

    Returns:
        Extracted text from the page body, cleaned of HTML tags.
    """
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style tags
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Collapse multiple blank lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
