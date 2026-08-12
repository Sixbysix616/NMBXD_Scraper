# NMBXD Scraper

A Python-based web scraper for **nmbxd1.com** (X岛匿名版), designed to **export and archive forum threads** in both **TXT** and **HTML** formats for offline viewing. The scraper automatically handles pagination, downloads embedded images, and preserves thread structure and metadata.

---

## Features

- **Multi-page thread scraping** - Automatically fetches all pages of a thread
- **Three export formats** (pick any combination):
  - **TXT**: Clean, readable text format with user IDs, timestamps, and post numbers
  - **HTML**: Formatted HTML with embedded images for offline viewing
  - **CSV**: One row per post (`floor, post_id, uid, is_po, time, body_text, image_urls`) for spreadsheet analysis. Written as UTF-8 with BOM so Excel opens Chinese correctly.
- **Image downloading** - Automatically downloads and embeds thread images locally
- **User identification** - Marks original poster (PO主) across all posts
- **Headless browser support** - Runs in background without opening browser windows
- **Error handling** - Robust error handling and timeout management

---

## Installation

### Prerequisites

- Python 3.7+
- Google Chrome browser (required for Selenium)

### Install Dependencies

```bash
pip install selenium beautifulsoup4 requests webdriver-manager
```

Or create a `requirements.txt` with:
```
selenium
beautifulsoup4
requests
webdriver-manager
```

Then install:
```bash
pip install -r requirements.txt
```

---

## Usage

### Basic Command

Run the scraper:
```bash
python selenium_scraper.py
```

### Interactive Prompts

1. **Enter thread ID**:
   ```
   请输入串号：
   > 12345678
   ```
   The thread ID is the number from the URL: `https://www.nmbxd1.com/t/12345678`

2. **Choose export formats** — three independent checkboxes (`TXT` / `HTML` / `CSV`), tick any combination. TXT and HTML are on by default; at least one must be selected.

   Note: images are only downloaded when **HTML** is selected. A CSV-only run records the original remote image URLs and downloads nothing.

### Example Session

```bash
$ python selenium_scraper.py
请输入串号：
> 58339933

请选择保存格式：
1. 仅保存 TXT
2. 仅保存 HTML
3. 同时保存 TXT 和 HTML
> 3

🌐 打开页面 https://www.nmbxd1.com/t/58339933?page=1
[DEBUG] 第 1 页抓到 21 层楼
📥 图片已保存：a1b2c3d4e5f6.jpg
🌐 打开页面 https://www.nmbxd1.com/t/58339933?page=2
[DEBUG] 第 2 页抓到 20 层楼
📄 已保存 TXT 文件：~/Downloads/nmbxd/58339933/58339933.txt
🌐 已保存 HTML 文件：~/Downloads/nmbxd/58339933/58339933.html

✅ 抓取完成，共 41 层楼
```

---

## Output

### Output Directory Structure

All files are saved to `~/Downloads/nmbxd/`:

```
~/Downloads/nmbxd/
└── 58339933/
    ├── 58339933.txt          # Text export
    ├── 58339933.html         # HTML export
    ├── 58339933.csv          # CSV export (one row per post)
    └── images/               # Downloaded images (HTML export only)
        ├── a1b2c3d4e5f6.jpg
        └── 7f8e9d0c1b2a.png
```

### TXT Format

Plain text format with metadata and content:

```
gN7KHJl 2025-01-15 12:34:56 No.58339933
这是主题帖的内容
可以有多行

kL9MnPq 2025-01-15 12:45:23 No.58340001
这是回复内容

gN7KHJl(PO主) 2025-01-15 13:01:42 No.58340123
PO主的回复会标记出来
```

### CSV Format

One row per post, header included:

```
floor,post_id,uid,is_po,time,body_text,image_urls
1,58339933,gN7KHJl,True,2025-01-15 12:34:56,"这是主题帖的内容
可以有多行",https://…/a1b2c3.jpg
2,58340001,kL9MnPq,False,2025-01-15 12:45:23,这是回复内容,
```

- `is_po` is `True` only for posts by the thread starter
- `image_urls` holds the original remote URLs, `;`-separated
- Multi-line post bodies are quoted, so they stay in a single cell

### HTML Format

Styled HTML with embedded images for offline viewing:

- Clean, readable formatting
- User IDs, timestamps, and post numbers
- Embedded images (stored in `images/` subfolder)
- PO主 identification
- Responsive design with proper spacing

---

## How It Works

1. **Selenium WebDriver** opens the thread URL in headless Chrome
2. **Waits for content** to load using explicit waits
3. **BeautifulSoup** parses the HTML structure
4. **Extracts post data**: User ID, timestamp, post number, and content
5. **Downloads images** from thread and saves locally with MD5 hash filenames
6. **Handles pagination** automatically until the last page
7. **Exports data** in selected format(s) to Downloads folder

---

## Technical Details

- **Browser**: Headless Chrome (auto-managed by webdriver-manager)
- **Parser**: BeautifulSoup4 with html.parser
- **Image naming**: MD5 hash of image URL to avoid duplicates
- **Encoding**: UTF-8 for proper Chinese character support
- **Timeout**: 10 seconds for page load

---

## Limitations

- Requires active internet connection
- Depends on current nmbxd1.com HTML structure
- May fail if site structure changes significantly
- Rate limiting not implemented (use responsibly)

---

## Future Improvements

- [ ] Add command-line argument support
- [ ] Implement rate limiting between requests
- [ ] Add GUI interface
- [ ] Support batch downloading of multiple threads
- [ ] Add progress bar for long threads
- [ ] Implement resume capability for interrupted downloads

---

## License

This project is for personal archival purposes only. Please respect the original forum's terms of service.
