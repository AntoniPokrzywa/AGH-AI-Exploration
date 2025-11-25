import os
import sys
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(base_dir))


import logging
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import shutil
from datetime import datetime
from agents.utils import clean_html, ocr
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import ScraperState
from langchain_core.messages import SystemMessage


load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

@tool
def facebook_login():
    """Logs into Facebook using credentials from environment variables."""
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    fb_login_url = os.getenv("FB_LOGIN_URL", "https://www.facebook.com/login")

    if not email or not password:
        logging.error("Missing FB_EMAIL or FB_PASSWORD env vars")
        return { "status": "error", "message": "Missing FB_EMAIL or FB_PASSWORD env vars"  }

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir= base_dir / "data" / "fb-data",
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
        page.goto(fb_login_url, wait_until="domcontentloaded")
        

        # If the login inputs are not visible, assume already logged in
        if page.locator('input[name="email"], #email').count() == 0:
            logging.info("Login form not found; Assuming already logged in.")
            ctx.close()
            return { "status": "success", "message": "Login form not found; Assuming already logged in."  }

        try:
            btn = page.locator('[aria-label="Allow all cookies"]:not([aria-disabled="true"])').first
            btn.wait_for(state="visible", timeout=7000)
            btn.click(force=True)
            page.wait_for_timeout(1500)
        except Exception:
            logging.info("Cookies banner not found or already handled.")

        logging.info("Submitting login form...")
        page.locator('input[name="email"], #email').first.fill(email)
        page.locator('input[name="pass"], #pass').first.fill(password)
        try:
            page.locator('button[name="login"], [data-testid="royal_login_button"], #loginbutton').first.click()
        except Exception:
            page.keyboard.press("Enter")
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        logging.info("Login attempt completed")
        ctx.close()
        return { "status": "success", "message": "Login attempt completed." }
    
@tool
def facebook_scrape(url):
    """Scrapes Facebook profile and returns parsed OCR string and HTML."""
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=base_dir / "data" / "fb-data",
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
            page.screenshot(path=base_dir / "data" / "screens" / f"debug_fb_scroll_{datetime.now().timestamp()}.png")
            page.mouse.wheel(0, 500)
            page.wait_for_timeout(2000)
        html = page.content()
        logging.info("Scrape completed; cleaning and saving output...")
        ocr_text = ocr(str(base_dir / "data" / "screens"))
        with open(base_dir / "data" / "facebook_scrape.html", "w", encoding="utf-8") as f:
            f.write(html)
        cleaned_html = clean_html(html)

        shutil.rmtree(str(base_dir / "data" / "screens"))
        os.makedirs(str(base_dir / "data" / "screens"), exist_ok=True)
        ctx.close()
        return { "status": "success", "messages": {"ocr": ocr_text, "html": cleaned_html} }


facebook_tools = [facebook_login, facebook_scrape]
facebook_tool_node = ToolNode(facebook_tools)
model_with_tools = llm.bind_tools(facebook_tools)

def facebook_node(state: ScraperState):
    system_prompt = """
    You are a Facebook Data Scraper Agent. Your task is to scrape data from a given Facebook profile URL.
    Use the facebook_login tool ALWAYS to ensure you are logged in
    ONLY after ensuring you are logged in use facebook_scrape tool to scrape the profile data.
    Return the scraped data in a structured format."""

    messages = [SystemMessage(content=system_prompt)] + [state["url"]] + state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}



  

if __name__ == "__main__":
    facebook_login()