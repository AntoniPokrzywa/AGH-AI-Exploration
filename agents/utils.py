from bs4 import BeautifulSoup

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text()
    text = text.replace("\n", "")
    return text.strip()