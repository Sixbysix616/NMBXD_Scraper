"""Parallel image downloading."""
import os
import hashlib
import concurrent.futures
from urllib.parse import urlparse

import requests

from .config import USER_AGENT, IMAGE_TIMEOUT, IMAGE_WORKERS

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def _download_one(img_url, images_dir):
    img_ext = os.path.splitext(urlparse(img_url).path)[-1] or ".jpg"
    img_filename = hashlib.md5(img_url.encode("utf-8")).hexdigest() + img_ext
    local_path = os.path.join(images_dir, img_filename)

    if os.path.exists(local_path):
        return img_url, img_filename

    try:
        r = _session.get(img_url, timeout=IMAGE_TIMEOUT)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(r.content)
            print(f"📥 图片已保存：{img_filename}")
            return img_url, img_filename
        print(f"⚠️ 下载失败Σ( ﾟдﾟ)：{img_url} - 状态码: {r.status_code}")
    except Exception as e:
        print(f"⚠️ 下载异常Σ( ﾟдﾟ)：{img_url} - {e}")
    return img_url, None


def download_images(img_urls, images_dir):
    """Download image URLs in parallel. Returns {url: local_filename}."""
    result = {}
    if not img_urls:
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=IMAGE_WORKERS) as executor:
        futures = [executor.submit(_download_one, u, images_dir) for u in img_urls]
        for future in concurrent.futures.as_completed(futures):
            img_url, filename = future.result()
            if filename:
                result[img_url] = filename
    return result
