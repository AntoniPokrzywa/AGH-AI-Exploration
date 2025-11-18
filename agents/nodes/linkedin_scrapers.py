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


def linkedin_login_node():
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    print(email, password)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=base_dir / "data" / "ln-data",
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
        url = os.getenv("LINKEDIN_LOGIN_URL")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        if page.locator('input[id="username"], #email').count() == 0:
            logging.info("Login form not found; Assuming already logged in.")
            ctx.close()
            return {
                "status": "success",
                "message": "Login form not found; Assuming already logged in."
            }

        logging.info("Submitting login form...")
        page.locator('input[id="username"], #email').first.fill(email)
        page.locator('input[id="password"], #pass').first.fill(password)

        try:
            page.locator('button[type="submit"], [data-litms-control-urn="login-submit"], #loginbutton').first.click()
        except Exception:
            page.keyboard.press("Enter")



def lindkedin_scrape(url):
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=base_dir / "data" / "ln-data",
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
            page.screenshot(path=base_dir / "data" / "screens" / f"debug_ln_scroll_{datetime.now().timestamp()}.png")
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

linkedin_login_node()
lindkedin_scrape("https://www.linkedin.com/in/antonipokrzywa/")

