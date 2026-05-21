"""Selenium browser lifecycle and page loading."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .config import MAX_PAGE_RETRIES, PAGE_LOAD_TIMEOUT, CONTENT_SELECTOR


def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )


def load_page(driver, url):
    """Load a URL with retry. Returns page HTML source, or None if all retries fail."""
    for attempt in range(1, MAX_PAGE_RETRIES + 1):
        try:
            driver.get(url)
            WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, CONTENT_SELECTOR))
            )
            return driver.page_source
        except Exception as e:
            print(f"⚠️ 第 {attempt} 次加载失败: {e}")
    return None
