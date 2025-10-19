
import os
import logging
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utils import clean_html

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

FB_PROFILE_ABOUT = "https://www.facebook.com/profile.php?id=100009725953759&sk=about"
FB_LOGIN_URL = "https://www.facebook.com/login"
user_data_dir = "./data/fb-data"


# Make it as a tool or node ( langgraph style )
# We can also think about combining both login and scrape into one node
# And making them async
# And improving error handling / code in general
def facebook_login_node():
    email = os.getenv("FB_EMAIL")
    password = os.getenv("FB_PASSWORD")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-notifications",
            ],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(FB_LOGIN_URL, wait_until="domcontentloaded")
        if not email or not password:
            raise RuntimeError("Missing FB_EMAIL or FB_PASSWORD env vars")

        # If the login inputs are not visible, assume already logged in
        if page.locator('input[name="email"], #email').count() == 0:
            logging.info("Login form not found; assuming already logged in.")
            ctx.close()
            return

        # Close cookies banner
        # TODO add fallback if doesnt show
        btn = page.locator('[aria-label="Allow all cookies"]:not([aria-disabled="true"])').first
        btn.wait_for(state="visible", timeout=7000)
        btn.click(force=True)
        page.wait_for_timeout(1500)

        logging.info("Submitting login form...")
        page.locator('input[name="email"], #email').first.fill(email)
        page.locator('input[name="pass"], #pass').first.fill(password)
        try:
            page.locator('button[name="login"], [data-testid="royal_login_button"], #loginbutton').first.click()
        except Exception:
            page.keyboard.press("Enter")

        # Give it a moment to complete redirects
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        logging.info("Login attempt completed; current URL: %s", page.url)
        ctx.close()


def facebook_scrape_node():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
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
        page.goto(FB_PROFILE_ABOUT, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        for _ in range(10):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(300)
        html = page.content()
        logging.info("Scrape completed; cleaning and saving output...")
        with open("fb_profile_about.html", "w", encoding="utf-8") as f:
            f.write(clean_html(html))
        ctx.close()


    
if __name__ == "__main__":
    facebook_login_node()
    facebook_scrape_node()

