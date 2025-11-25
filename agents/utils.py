from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import os
from mistralai import Mistral
from dotenv import load_dotenv
import base64

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text()
    text = text.replace("\n", "")
    return text.strip()

def get_links(html: str) -> list:
    soup = BeautifulSoup(html, 'html.parser')
    hrefs = [a.get('href') for a in soup.find_all('a', href=True)]
    return hrefs


def encode_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')
        
def ocr(image_folder_path: str) -> None:
    load_dotenv()

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in .env")

    model = "mistral-small-latest"
    client = Mistral(api_key=api_key)

    
    for image_file in os.listdir(image_folder_path):
        image_path = os.path.join(image_folder_path, image_file)

        try:
            base64_image = encode_image(image_path)
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """return markdown format of the OCRed text from the image, if there is a photo without text
                                    -describe what is shown  on the photo in a concise way in format {photo: description inplace}. 
                                    Don't add image_url to markdown, only descriptions. Dont wrap answer in codeblock."""
                        },
                        {
                            "type": "document_url",
                            "document_url": f"data:image/png;base64,{base64_image}" 
                        }
                    ]
                }
            ]
            
            chat_response = client.chat.complete(
                model=model,
                messages=messages
            )
            
            with open(f"result_{image_file}.md", "w", encoding="utf-8") as f:
                if hasattr(chat_response, "pages") and chat_response.pages:
                    for page in chat_response.pages:
                        f.write(f"# Strona {page.index}\n\n")
                        f.write(page.markdown)
                        f.write("\n\n")
                elif hasattr(chat_response, "choices"):
                    f.write(chat_response.choices[0].message.content)
                else:
                    f.write(str(chat_response)[8:])
                    
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")