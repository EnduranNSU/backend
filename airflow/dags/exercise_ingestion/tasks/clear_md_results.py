import re

def md_to_text(md: str) -> str:
    text = md

    text = re.sub(r'#+\s*', '', text)

    text = re.sub(r'(\*{1,2}|_{1,2})', '', text)

    text = re.sub(r'-{3,}', '', text)

    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)

    text = text.strip()

    return text