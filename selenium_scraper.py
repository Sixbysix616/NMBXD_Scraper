from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import textwrap

def get_downloads_dir():
    return os.path.join(os.path.expanduser("~"), "Downloads", "nmbxd")

def save_as_html(thread_id, posts_html, html_path):
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{thread_id} - X岛离线存档</title>
    <style>
        body {{ font-family: sans-serif; background: #f9f9f9; padding: 20px; }}
        .post {{ background: white; margin: 1em auto; padding: 1em; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 800px; }}
        .meta {{ font-size: 0.9em; color: #666; margin-bottom: 0.5em; }}
        .content {{ font-size: 1.1em; line-height: 1.6; white-space: pre-wrap; }}
    </style>
</head>
<body>
    <h1>串 {thread_id} 离线存档</h1>
    {"".join(posts_html)}
</body>
</html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_template)

def fetch_thread(thread_id, save_txt=True, save_html=False):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    page = 1
    all_posts = []
    html_posts = []
    first_uid = None

    while True:
        url = f"https://www.nmbxd1.com/t/{thread_id}?page={page}"
        print(f"🌐 打开页面 {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".h-threads-content"))
            )
        except Exception as e:
            print(f"❌ 页面加载失败: {e}")
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = []

        if page == 1:
            main = soup.select_one(".h-threads-item-main")
            if main:
                posts.append(main)

        posts += soup.select(".h-threads-item-reply")
        print(f"[DEBUG] 第 {page} 页抓到 {len(posts)} 层楼")

        if not posts:
            break

        for i, post in enumerate(posts):
            content = post.select_one(".h-threads-content")
            info = post.select_one(".h-threads-info")

            if not (content and info):
                continue

            post_id = info.select_one(".h-threads-info-id")
            post_time = info.select_one(".h-threads-info-createdat")
            post_uid = info.select_one(".h-threads-info-uid")

            if not post_id or not post_time or not post_uid:
                continue

            id_text = post_id.get_text(strip=True).replace("No.", "")
            time_text = post_time.get_text(strip=True)
            uid_text = post_uid.get_text(strip=True)

            if uid_text.strip() == "Tips" or time_text.startswith("2099"):
                continue

            if page == 1 and i == 0:
                first_uid = uid_text

            is_po = "(PO主)" if uid_text == first_uid else ""
            header = f"{uid_text}{is_po} {time_text} No.{id_text}".strip()
            body_text = content.get_text("\n", strip=True)

            all_posts.append(f"{header}\n{body_text}")

            body_html = ''.join(str(tag).strip() for tag in content.contents).strip()
            html_post = f'<div class="post"><div class="meta">{header}</div><div class="content">{body_html}</div></div>'
            #html_post = f"""
            #<div class="post">
            #### """
            html_posts.append(html_post)

        pagination = soup.select_one(".uk-pagination")
        has_next = pagination and any("下一页" in a.get_text() for a in pagination.select("a"))
        if not has_next:
           break

        page += 1

    driver.quit()
    thread_dir = os.path.join(get_downloads_dir(), str(thread_id))
    os.makedirs(thread_dir, exist_ok=True)

    if save_txt:
        txt_path = os.path.join(thread_dir, f"{thread_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_posts))
        print(f"📄 已保存 TXT 文件：{txt_path}")

    if save_html:
        html_path = os.path.join(thread_dir, f"{thread_id}.html")
        save_as_html(thread_id, html_posts, html_path)
        print(f"🌐 已保存 HTML 文件：{html_path}")

    print(f"\n✅ 抓取完成，共 {len(all_posts)} 层楼")

if __name__ == "__main__":
    tid = input("请输入串号：\n> ").strip()
    print("\n请选择保存格式：")
    print("1. 仅保存 TXT")
    print("2. 仅保存 HTML")
    print("3. 同时保存 TXT 和 HTML")

    mode = input("> ").strip()
    if mode not in {"1", "2", "3"}:
        print("❌ 无效选择，默认保存 TXT")
        mode = "1"

    fetch_thread(tid, save_txt=(mode in {"1", "3"}), save_html=(mode in {"2", "3"}))
