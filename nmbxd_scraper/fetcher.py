"""HTTP page fetching with retry."""
import requests

from .config import MAX_PAGE_RETRIES, PAGE_TIMEOUT, USER_AGENT

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def fetch_page(url):
    """Fetch a URL's HTML with retry. Returns HTML text, or None if all retries fail."""
    for attempt in range(1, MAX_PAGE_RETRIES + 1):
        try:
            r = _session.get(url, timeout=PAGE_TIMEOUT)
            if r.status_code == 200:
                r.encoding = "utf-8"
                return r.text
            print(f"⚠️ 第 {attempt} 次加载失败: HTTP {r.status_code}")
        except Exception as e:
            print(f"⚠️ 第 {attempt} 次加载失败: {e}")
    return None
