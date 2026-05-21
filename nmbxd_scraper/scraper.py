"""Thread scraping orchestration."""
import os

from .config import THREAD_URL
from .storage import (
    get_thread_dir,
    ensure_thread_dirs,
    save_checkpoint,
    load_checkpoint,
    clear_checkpoint,
)
from .browser import create_driver, load_page
from .parser import parse_page
from .images import download_images
from .exporters import render_txt_entry, render_html_post, write_txt, write_html


def _resume_or_fresh(thread_id):
    """Return (start_page, first_uid, floor_counter, all_posts, html_posts)."""
    checkpoint = load_checkpoint(thread_id)
    if checkpoint:
        prompt = (
            f"🔄 发现第 {checkpoint['page']} 页的未完成记录"
            f"（已有 {len(checkpoint['all_posts'])} 层楼），是否继续？(y/n) > "
        )
        if input(prompt).strip().lower() == "y":
            print(f"▶️ 从第 {checkpoint['page'] + 1} 页继续抓取")
            return (
                checkpoint["page"] + 1,
                checkpoint.get("first_uid"),
                checkpoint["floor_counter"],
                checkpoint["all_posts"],
                checkpoint["html_posts"],
            )
    return 1, None, 0, [], []


def fetch_thread(thread_id, save_txt=True, save_html=False):
    images_dir = ensure_thread_dirs(thread_id)
    thread_dir = get_thread_dir(thread_id)

    page, first_uid, floor_counter, all_posts, html_posts = _resume_or_fresh(thread_id)

    driver = create_driver()
    try:
        while True:
            url = THREAD_URL.format(thread_id=thread_id, page=page)
            print(f"🌐 打开页面 {url}")

            page_source = load_page(driver, url)
            if page_source is None:
                print("❌ 页面加载失败，停止抓取")
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
                is_po = "(PO主)" if post.uid == first_uid else ""
                meta_text = f"{post.uid}{is_po} {post.time} No.{post.post_id}".strip()

                all_posts.append(
                    render_txt_entry(floor_counter, meta_text, post.body_text, post.image_urls)
                )
                if save_html:
                    html_posts.append(
                        render_html_post(
                            floor_counter, post.post_id, meta_text, post.raw_html, img_map
                        )
                    )

            save_checkpoint(thread_id, {
                "page": page,
                "first_uid": first_uid,
                "floor_counter": floor_counter,
                "all_posts": all_posts,
                "html_posts": html_posts,
            })

            if not result.has_next:
                break
            page += 1
    finally:
        driver.quit()

    if save_txt:
        txt_path = os.path.join(thread_dir, f"{thread_id}.txt")
        write_txt(all_posts, txt_path)
        print(f"📄 已保存 TXT 文件：{txt_path}")

    if save_html:
        html_path = os.path.join(thread_dir, f"{thread_id}.html")
        write_html(thread_id, html_posts, html_path)
        print(f"🌐 已保存 HTML 文件：{html_path}")

    clear_checkpoint(thread_id)
    print(f"\n✅ 抓取完成，共 {len(all_posts)} 层楼")
