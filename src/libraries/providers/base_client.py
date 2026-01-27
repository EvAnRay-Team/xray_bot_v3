from typing import Optional, Dict
import httpx


class BaseClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=10.0
        )
# HEADERS = {"Authorization": LXNSAUTH} 落雪