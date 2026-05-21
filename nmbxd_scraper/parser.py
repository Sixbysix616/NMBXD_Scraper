"""Parse nmbxd thread page HTML into structured Post objects."""
from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag

from .config import IMG_EXTENSIONS


@dataclass
class Post:
    post_id: str
    uid: str
    time: str
    body_text: str
    image_urls: List[str]
    raw_html: str


@dataclass
class PageResult:
    posts: List[Post]
    has_next: bool
    raw_count: int


def parse_page(page_source, include_main):
    """Parse a page's HTML source into a PageResult."""
    soup = BeautifulSoup(page_source, "html.parser")

    elements = []
    if include_main:
        main = soup.select_one(".h-threads-item-main")
        if main:
            elements.append(main)
    elements += soup.select(".h-threads-item-reply")

    posts = [p for p in (_parse_post(el) for el in elements) if p]
    return PageResult(posts=posts, has_next=_has_next_page(soup), raw_count=len(elements))


def _parse_post(post):
    content = post.select_one(".h-threads-content")
    info = post.select_one(".h-threads-info")
    if not (content and info):
        return None

    post_id_el = info.select_one(".h-threads-info-id")
    time_el = info.select_one(".h-threads-info-createdat")
    uid_el = info.select_one(".h-threads-info-uid")
    if not post_id_el or not time_el or not uid_el:
        return None

    time_text = time_el.get_text(strip=True)
    uid_text = uid_el.get_text(strip=True)
    if uid_text.strip() == "Tips" or time_text.startswith("2099"):
        return None

    return Post(
        post_id=post_id_el.get_text(strip=True).replace("No.", ""),
        uid=uid_text,
        time=time_text,
        body_text=content.get_text("\n", strip=True),
        image_urls=_extract_image_urls(post),
        raw_html=str(post),
    )


def _extract_image_urls(post):
    urls = []
    for a_tag in post.find_all("a", class_="h-threads-img-a"):
        if not isinstance(a_tag, Tag):
            continue
        href = a_tag.get("href")
        img_url = str(href) if href else ""
        if img_url and img_url.endswith(IMG_EXTENSIONS):
            urls.append(img_url)
    return urls


def _has_next_page(soup):
    pagination = soup.select_one(".uk-pagination")
    if not pagination:
        return False
    return any("下一页" in a.get_text() for a in pagination.select("a"))
