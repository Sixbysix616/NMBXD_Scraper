"""Render parsed posts into TXT and HTML output."""
import re

from bs4 import BeautifulSoup
from bs4.element import Tag


def linkify_quotes(html_str):
    """Turn &gt;&gt;No.XXXXX quote markers into clickable anchor links."""
    return re.sub(r'&gt;&gt;No\.(\d+)', r'<a href="#post-\1">&gt;&gt;No.\1</a>', html_str)


def render_txt_entry(floor, meta_text, body_text, image_urls):
    entry = f"#{floor} {meta_text}\n{body_text}"
    if image_urls:
        entry += "\n" + "\n".join(f"[图片: {u}]" for u in image_urls)
    return entry


def render_html_post(floor, post_id, meta_text, raw_html, img_url_to_filename):
    body_html = linkify_quotes(_localize_images(raw_html, img_url_to_filename))
    return (
        f'<div class="post" id="post-{post_id}">'
        f'<div class="meta"><span class="floor">#{floor}</span> {meta_text}</div>'
        f'<div class="content">{body_html}</div>'
        f'</div>'
    )


def _localize_images(raw_html, img_url_to_filename):
    """Re-parse a post's HTML, swap image links to local paths, return content HTML."""
    soup_post = BeautifulSoup(raw_html, "html.parser")
    for a_tag in soup_post.find_all("a", class_="h-threads-img-a"):
        if not isinstance(a_tag, Tag):
            continue
        href = a_tag.get("href")
        img_url = str(href) if href else ""
        local_src = (
            f"images/{img_url_to_filename[img_url]}"
            if img_url in img_url_to_filename
            else img_url
        )
        a_tag.replace_with(soup_post.new_tag("img", src=local_src))
    soup_content = soup_post.select_one(".h-threads-content")
    return ''.join(str(tag).strip() for tag in soup_content.contents).strip()


def write_txt(posts_txt, txt_path):
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(posts_txt))


def write_html(thread_id, posts_html, html_path):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{thread_id} - X岛离线存档</title>
    <style>
        body {{ font-family: sans-serif; background: #f9f9f9; padding: 20px; }}
        .post {{ background: white; margin: 1em auto; padding: 1em; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 800px; }}
        .meta {{ font-size: 0.9em; color: #666; margin-bottom: 0.5em; }}
        .floor {{ font-weight: bold; color: #333; margin-right: 0.5em; }}
        .content {{ font-size: 1.1em; line-height: 1.6; white-space: pre-wrap; }}
        .content a {{ color: #0077cc; text-decoration: none; }}
        .content a:hover {{ text-decoration: underline; }}
        .content img {{ max-width: 100%; height: auto; display: block; margin: 0.5em 0; }}
    </style>
</head>
<body>
    <h1>串 {thread_id} 离线存档</h1>
    {"".join(posts_html)}
</body>
</html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
