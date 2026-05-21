"""Shared configuration constants."""

# Page loading
MAX_PAGE_RETRIES = 3
PAGE_LOAD_TIMEOUT = 10  # seconds

# Image downloading
IMAGE_TIMEOUT = 10  # seconds
IMAGE_WORKERS = 8
IMG_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# HTTP
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Site
THREAD_URL = "https://www.nmbxd1.com/t/{thread_id}?page={page}"
CONTENT_SELECTOR = ".h-threads-content"
