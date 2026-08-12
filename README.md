# NMBXD Scraper

A Python desktop tool for **nmbxd1.com** (X岛匿名版) that **exports and archives forum threads** as **TXT**, **HTML**, and **CSV** for offline use. It walks every page of a thread, downloads embedded images, and preserves post metadata.

No browser automation involved — thread pages are server-rendered, so a plain HTTP request returns the complete HTML. That keeps the tool fast, dependency-light, and packageable into a standalone `.exe`.

---

## Features

- **Multi-page thread scraping** — follows pagination automatically until the last page
- **Three export formats**, tick any combination:
  - **TXT** — clean, readable text with user IDs, timestamps, and post numbers
  - **HTML** — self-contained offline archive with locally embedded images and a paginated viewer
  - **CSV** — one row per post for spreadsheet analysis, UTF-8 with BOM so Excel opens Chinese correctly
- **Parallel image downloading** — 8 concurrent workers, deduplicated by MD5 of the URL
- **Resume support** — a checkpoint is saved after every page, so an interrupted run can pick up where it left off
- **PO主 identification** — posts by the thread starter are marked across all formats
- **Ad filtering** — sponsored "Tips" posts are dropped
- **GUI** — tkinter window with a live log; no command line needed
- **Polite by default** — 1 second between page requests, retries on failure

---

## Installation

### Prerequisites

- Python 3.7+

### Install Dependencies

```bash
pip install -r requirements.txt
```

Just two packages: `requests` and `beautifulsoup4`.

---

## Usage

Run from the project root:

```bash
python main.py
```

A window opens with four things to set:

1. **串号 (thread ID)** — the number from the thread URL, e.g. `58339933` in `https://www.nmbxd1.com/t/58339933`. Digits only.
2. **保存格式** — three independent checkboxes: `TXT` / `HTML` / `CSV`. TXT and HTML are ticked by default; at least one is required.
3. **选择保存文件夹** — defaults to `~/Downloads/nmbxd`, changeable.
4. **开始抓取** — progress streams into the log pane below. The output folder opens automatically when the run finishes.

If an unfinished run is detected for the same thread ID, a dialog offers to resume from where it stopped.

> **Note:** images are only downloaded when **HTML** is selected. A CSV-only or TXT-only run records the original remote image URLs and downloads nothing.

### Example Log Output

```
🌐 抓取页面 https://www.nmbxd1.com/t/58339933?page=1
[DEBUG] 第 1 页抓到 21 层楼
📥 图片已保存：a1b2c3d4e5f6.jpg
🌐 抓取页面 https://www.nmbxd1.com/t/58339933?page=2
[DEBUG] 第 2 页抓到 20 层楼
📄 已保存 TXT 文件：C:\Users\you\Downloads\nmbxd\58339933\58339933.txt
🌐 已保存 HTML 文件：C:\Users\you\Downloads\nmbxd\58339933\58339933.html
📊 已保存 CSV 文件：C:\Users\you\Downloads\nmbxd\58339933\58339933.csv

✅ 抓取完成(ゝ∀･)，共 41 层楼
```

---

## Output

### Directory Structure

```
~/Downloads/nmbxd/
└── 58339933/
    ├── 58339933.txt          # Text export
    ├── 58339933.html         # HTML export
    ├── 58339933.csv          # CSV export (one row per post)
    ├── .checkpoint.json      # Resume state; deleted when the run completes
    └── images/               # Downloaded images (HTML export only)
        ├── a1b2c3d4e5f6.jpg
        └── 7f8e9d0c1b2a.png
```

### TXT Format

```
#1 gN7KHJl(PO主) 2025-01-15 12:34:56 No.58339933
这是主题帖的内容
可以有多行
[图片: https://image.nmb.best/image/…/a1b2c3.jpg]

#2 kL9MnPq 2025-01-15 12:45:23 No.58340001
这是回复内容
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
- Multi-line bodies are quoted, so they stay inside a single cell
- Encoded as UTF-8 with BOM — double-click opens correctly in Excel; from pandas use `encoding="utf-8-sig"`

### HTML Format

A single self-contained file with locally embedded images:

- 19 posts per page, with a client-side pagination bar (no server needed)
- `>>No.12345` quote markers become links that jump to the quoted post, switching pages if necessary
- User IDs, timestamps, post numbers, and PO主 marks preserved

---

## How It Works

1. **Fetch** — `requests.Session` requests each page with a browser User-Agent, retrying up to 3 times
2. **Parse** — BeautifulSoup extracts `.h-threads-item-main` and `.h-threads-item-reply` blocks
3. **Filter** — sponsored posts (uid `Tips`, or timestamps starting `2099`) are dropped
4. **Download images** — in parallel, but only when HTML output is requested
5. **Mark PO主** — the first post's uid identifies the thread starter
6. **Checkpoint** — progress is written to disk after every page
7. **Paginate** — continues while the pagination bar still offers 下一页
8. **Export** — writes the selected formats into the thread folder

Because the site is server-rendered, step 1 gets the full post list in a single HTTP response — no headless browser, no JavaScript execution, no WebDriver.

---

## Project Layout

```
main.py                  # tkinter GUI entry point
nmbxd_scraper/
├── config.py            # tunable constants (timeouts, delays, worker count)
├── fetcher.py           # HTTP GET with retry, shared session
├── parser.py            # HTML → Post dataclass
├── images.py            # parallel image downloading
├── exporters.py         # TXT / HTML / CSV rendering and writing
├── storage.py           # paths and resume checkpoint
└── scraper.py           # orchestration
```

---

## Technical Details

All tunables live in [`nmbxd_scraper/config.py`](nmbxd_scraper/config.py):

| Setting | Value | Meaning |
| --- | --- | --- |
| `PAGE_TIMEOUT` | 10s | Per HTTP request, not per page load |
| `MAX_PAGE_RETRIES` | 3 | Retries before giving up on a page |
| `REQUEST_DELAY` | 1.0s | Pause between page requests |
| `IMAGE_TIMEOUT` | 10s | Per image download |
| `IMAGE_WORKERS` | 8 | Concurrent image downloads |
| `POSTS_PER_PAGE` | 19 | Posts per page in the HTML archive |

- **HTTP client**: `requests.Session` with connection reuse
- **Parser**: BeautifulSoup4 with `html.parser`
- **Image naming**: MD5 of the image URL, so re-runs skip existing files
- **Encoding**: UTF-8 throughout; UTF-8 with BOM for CSV

---

## Building a Standalone Executable

[`NMBXD_Scraper.spec`](NMBXD_Scraper.spec) is set up for PyInstaller:

```bash
pip install pyinstaller
pyinstaller NMBXD_Scraper.spec
```

The result lands in `dist/NMBXD_Scraper.exe` and needs no Python installation on the target machine.

---

## Limitations

- Requires an active internet connection
- Depends on the current nmbxd1.com HTML structure; may break if the site changes
- If a page fetch fails mid-run, the checkpoint is still cleared, so resume only works after a hard interruption (e.g. closing the window)
- One thread at a time

---

## Future Improvements

- [ ] Command-line argument support (currently GUI-only)
- [ ] Batch downloading of multiple threads
- [ ] Progress bar for long threads
- [ ] Preserve the checkpoint when a run ends on a fetch failure

---

## License

This project is for personal archival purposes only. Please respect the original forum's terms of service.
