"""Thread scraping orchestration."""
import os
import time

from .config import THREAD_URL, REQUEST_DELAY
from .storage import (
    get_default_output_dir,
    get_thread_dir,
    ensure_thread_dirs,
    save_checkpoint,
    load_checkpoint,
    clear_checkpoint,
)
from .fetcher import fetch_page
from .parser import parse_page
from .images import download_images
from .exporters import (
    render_txt_entry,
    render_html_post,
    render_csv_row,
    write_txt,
    write_html,
    write_csv,
)


def _load_state(thread_dir, resume, save_csv):
    """Return (start_page, first_uid, floor_counter, all_posts, html_posts, csv_rows)."""
    if resume:
        checkpoint = load_checkpoint(thread_dir)
        if checkpoint:
            print(f"▶️ 从第 {checkpoint['page'] + 1} 页继续抓取(つд⊂)")
            if save_csv and "csv_rows" not in checkpoint and checkpoint["floor_counter"]:
                print(
                    "⚠️ 这份记录是加入 CSV 功能之前留下的，已抓过的楼层进不了 CSV。\n"
                    "   想要完整的 CSV 请不要续抓，重新完整抓一次。"
                )
            return (
                checkpoint["page"] + 1,
                checkpoint.get("first_uid"),
                checkpoint["floor_counter"],
                checkpoint["all_posts"],
                checkpoint["html_posts"],
                checkpoint.get("csv_rows", []),
            )
    return 1, None, 0, [], [], []


def fetch_thread(thread_id, save_txt=True, save_html=False, save_csv=False,
                 output_dir=None, resume=False):
    """Scrape a thread into output_dir/{thread_id}/. Returns that thread directory."""
    if output_dir is None:
        output_dir = get_default_output_dir()
    thread_dir = get_thread_dir(output_dir, thread_id)
    images_dir = ensure_thread_dirs(thread_dir)

    page, first_uid, floor_counter, all_posts, html_posts, csv_rows = _load_state(
        thread_dir, resume, save_csv
    )

    while True:
        url = THREAD_URL.format(thread_id=thread_id, page=page)
        print(f"🌐 抓取页面 {url}")

        page_source = fetch_page(url)
        if page_source is None:
            print("❌ 页面加载失败(ﾟДﾟ≡ﾟДﾟ)，停止抓取")
            break

        result = parse_page(page_source, include_main=(page == 1))
        print(f"[DEBUG] 第 {page} 页抓到 {result.raw_count} 层楼")
        if result.raw_count == 0:
            break

        img_map = {}
        if save_html:
            urls = {u for p in result.posts for u in p.image_urls}
            img_map = download_images(urls, images_dir)

        for post in result.posts:
            if first_uid is None:
                first_uid = post.uid
            floor_counter += 1
            is_po = post.uid == first_uid
            po_mark = "(PO主)" if is_po else ""
            meta_text = f"{post.uid}{po_mark} {post.time} No.{post.post_id}".strip()

            all_posts.append(
                render_txt_entry(floor_counter, meta_text, post.body_text, post.image_urls)
            )
            if save_html:
                html_posts.append(
                    render_html_post(post.post_id, meta_text, post.raw_html, img_map)
                )
            if save_csv:
                csv_rows.append(render_csv_row(floor_counter, post, is_po))

        save_checkpoint(thread_dir, {
            "page": page,
            "first_uid": first_uid,
            "floor_counter": floor_counter,
            "all_posts": all_posts,
            "html_posts": html_posts,
            "csv_rows": csv_rows,
        })

        if not result.has_next:
            break
        page += 1
        time.sleep(REQUEST_DELAY)

    if save_txt:
        txt_path = os.path.join(thread_dir, f"{thread_id}.txt")
        write_txt(all_posts, txt_path)
        print(f"📄 已保存 TXT 文件：{txt_path}")

    if save_html:
        html_path = os.path.join(thread_dir, f"{thread_id}.html")
        write_html(thread_id, html_posts, html_path)
        print(f"🌐 已保存 HTML 文件：{html_path}")

    if save_csv:
        csv_path = os.path.join(thread_dir, f"{thread_id}.csv")
        write_csv(csv_rows, csv_path)
        print(f"📊 已保存 CSV 文件：{csv_path}")

    clear_checkpoint(thread_dir)
    print(f"\n✅ 抓取完成(ゝ∀･)，共 {len(all_posts)} 层楼")
    return thread_dir
