import sys
from datetime import datetime
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(base_dir))

import os
import logging
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from agents.utils import clean_html, ocr
import shutil

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def instagram_login():
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    print(email, password)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=base_dir / "data" / "ig-data",
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-notifications",
            ],
        )

        page = ctx.new_page()
        url = os.getenv("INSTAGRAM_LOGIN_URL")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        try:
            btn = page.locator("button", has_text="Allow all cookies").first
            btn.wait_for(state="visible", timeout=7000)
            btn.click(force=True)
            page.wait_for_timeout(1500)
        except Exception:
            logging.info("Cookies banner not found or already handled.")

        if page.locator('input[name="email"], #email').count() == 0 and page.locator('input[name="username"]').count() == 0:
            logging.info("Login form not found; Assuming already logged in.")
            ctx.close()
            return {
                "status": "success",
                "message": "Login form not found; Assuming already logged in."
            }

        logging.info("Submitting login form...")
        if page.locator('input[name="username"]').count() > 0:
            page.locator('input[name="username"]').first.fill(email)
        else:
            page.locator('input[name="email"], #email').first.fill(email)
        
        if page.locator('input[name="pass"], #pass').count() > 0:
            page.locator('input[name="pass"], #pass').first.fill(password)
            btn = page.locator("span", has_text="Log in").first.click()
        else:
            page.locator('input[name="password"]').first.fill(password)
            btn = page.locator('button[type="submit"]').first.click()



        page.wait_for_timeout(20000)


def instagram_scrape(url):
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=base_dir / "data" / "ig-data",
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-notifications",
            ],
        )
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        for _ in range(6):
            page.screenshot(path=base_dir / "data" / "screens" / f"debug_ig_scroll_{datetime.now().timestamp()}.png")
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(2000)
        html = page.content()
        logging.info("Scrape completed; cleaning and saving output...")
        ocr_text = ocr(str(base_dir / "data" / "screens"))
        cleaned_html = clean_html(html)


        shutil.rmtree(str(base_dir / "data" / "screens"))
        os.makedirs(str(base_dir / "data" / "screens"), exist_ok=True)
        ctx.close()
        return { "status": "success"} #"messages": {"ocr": ocr_text, "html": cleaned_html} }
#instagram_login()
instagram_scrape("https://www.instagram.com/cristiano/")

