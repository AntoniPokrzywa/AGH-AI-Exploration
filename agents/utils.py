from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import os

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text()
    text = text.replace("\n", "")
    return text.strip()

def ocr(image_foler_path: str):
    output=""
    for image_file in os.listdir(image_foler_path):
        image_path = os.path.join(image_foler_path, image_file)
        output+=pytesseract.image_to_string(Image.open(image_path))#, lang="pol")  # możesz zmienić na "eng" itd.
    return output