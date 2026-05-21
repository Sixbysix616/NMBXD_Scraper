"""Render parsed posts into TXT and HTML output."""
import re

from bs4 import BeautifulSoup
from bs4.element import Tag

from .config import POSTS_PER_PAGE


def linkify_quotes(html_str):
    """Turn >>No.XXXXX quote markers into clickable anchor links."""
    return re.sub(r'>>No\.(\d+)', r'<a href="#post-\1">&gt;&gt;No.\1</a>', html_str)


def render_txt_entry(floor, meta_text, body_text, image_urls):
    entry = f"#{floor} {meta_text}\n{body_text}"
    if image_urls:
        entry += "\n" + "\n".join(f"[图片: {u}]" for u in image_urls)
    return entry


def render_html_post(post_id, meta_text, raw_html, img_url_to_filename):
    body_html = linkify_quotes(_localize_images(raw_html, img_url_to_filename))
    return (
        f'<div class="post" id="post-{post_id}">'
        f'<div class="meta">{meta_text}</div>'
        f'<div class="content">{body_html}</div>'
        f'</div>'
    )


def _localize_images(raw_html, img_url_to_filename):
    """Re-parse a post's HTML and return body HTML: text, then localized images.

    Image links (.h-threads-img-a) live in .h-threads-img-box, a sibling of the
    text container .h-threads-content, so they must be collected separately
    instead of just returning the content element's children.
    """
    soup_post = BeautifulSoup(raw_html, "html.parser")

    images_html = []
    for a_tag in soup_post.find_all("a", class_="h-threads-img-a"):
        if not isinstance(a_tag, Tag):
            continue
        href = a_tag.get("href")
        img_url = str(href) if href else ""
        if not img_url:
            continue
        local_src = (
            f"images/{img_url_to_filename[img_url]}"
            if img_url in img_url_to_filename
            else img_url
        )
        images_html.append(f'<img src="{local_src}">')

    content = soup_post.select_one(".h-threads-content")
    text_html = ""
    if content:
        text_html = "".join(str(tag).strip() for tag in content.contents).strip()

    return text_html + "".join(images_html)


def write_txt(posts_txt, txt_path):
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(posts_txt))


def write_html(thread_id, posts_html, html_path):
    chunks = [
        posts_html[i:i + POSTS_PER_PAGE]
        for i in range(0, len(posts_html), POSTS_PER_PAGE)
    ]
    body_parts = []
    for idx, chunk in enumerate(chunks, start=1):
        hidden = "" if idx == 1 else ' style="display:none"'
        body_parts.append(
            f'<div class="page" data-page="{idx}"{hidden}>{"".join(chunk)}</div>'
        )

    html = (
        _HTML_TEMPLATE
        .replace("%%THREAD_ID%%", str(thread_id))
        .replace("%%BODY%%", "".join(body_parts))
    )
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>%%THREAD_ID%% - X岛离线存档</title>
    <style>
        body { font-family: sans-serif; background: #f9f9f9; padding: 20px; }
        h1 { text-align: center; }
        .post { background: white; margin: 1em auto; padding: 1em; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 800px; }
        .meta { font-size: 0.9em; color: #666; margin-bottom: 0.5em; }
        .content { font-size: 1.1em; line-height: 1.6; white-space: pre-wrap; }
        .content a { color: #0077cc; text-decoration: none; }
        .content a:hover { text-decoration: underline; }
        .content img { max-width: 100%; height: auto; display: block; margin: 0.5em 0; }
        .pagination { text-align: center; margin: 1.2em 0; }
        .pg-btn { display: inline-block; padding: 0.3em 0.7em; margin: 0 2px; border-radius: 4px; background: #fff; color: #0077cc; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.1); user-select: none; }
        .pg-btn.active { background: #0077cc; color: #fff; cursor: default; }
        .pg-btn.disabled { color: #bbb; cursor: default; box-shadow: none; }
        .pg-ellipsis { display: inline-block; padding: 0.3em 0.4em; color: #999; }
    </style>
</head>
<body>
    <h1>串 %%THREAD_ID%% 离线存档</h1>
    <div class="pagination"></div>
    <div id="posts">%%BODY%%</div>
    <div class="pagination"></div>
    <script>
    (function () {
      var pages = document.querySelectorAll('#posts .page');
      var bars = document.querySelectorAll('.pagination');
      var total = pages.length;
      var current = 1;

      if (total <= 1) {
        bars.forEach(function (b) { b.style.display = 'none'; });
        return;
      }

      function pageList() {
        var keep = {};
        keep[1] = true;
        keep[total] = true;
        for (var i = current - 2; i <= current + 2; i++) {
          if (i >= 1 && i <= total) keep[i] = true;
        }
        var nums = Object.keys(keep).map(Number).sort(function (a, b) { return a - b; });
        var out = [];
        var prev = 0;
        nums.forEach(function (n) {
          if (n - prev > 1) out.push('...');
          out.push(n);
          prev = n;
        });
        return out;
      }

      function makeBtn(label, opts) {
        var el = document.createElement('span');
        el.className = 'pg-btn';
        el.textContent = label;
        if (opts.disabled) {
          el.className += ' disabled';
        } else if (opts.active) {
          el.className += ' active';
        } else {
          el.onclick = opts.onclick;
        }
        return el;
      }

      function buildBar(bar) {
        bar.innerHTML = '';
        bar.appendChild(makeBtn('上一页', {
          disabled: current === 1,
          onclick: function () { go(current - 1); }
        }));
        pageList().forEach(function (n) {
          if (n === '...') {
            var e = document.createElement('span');
            e.className = 'pg-ellipsis';
            e.textContent = '…';
            bar.appendChild(e);
          } else {
            bar.appendChild(makeBtn(String(n), {
              active: n === current,
              onclick: function () { go(n); }
            }));
          }
        });
        bar.appendChild(makeBtn('下一页', {
          disabled: current === total,
          onclick: function () { go(current + 1); }
        }));
      }

      function render() {
        pages.forEach(function (p, i) {
          p.style.display = (i + 1 === current) ? '' : 'none';
        });
        bars.forEach(buildBar);
      }

      function go(n, toTop) {
        if (n < 1 || n > total) return;
        current = n;
        render();
        if (toTop !== false) window.scrollTo(0, 0);
      }

      document.addEventListener('click', function (e) {
        var a = e.target.closest ? e.target.closest('a[href^="#post-"]') : null;
        if (!a) return;
        var target = document.getElementById(a.getAttribute('href').slice(1));
        if (!target) return;
        e.preventDefault();
        var pageDiv = target.closest('.page');
        if (pageDiv) go(parseInt(pageDiv.getAttribute('data-page'), 10), false);
        target.scrollIntoView();
      });

      render();
    })();
    </script>
</body>
</html>
"""
