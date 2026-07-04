# utils/source_compressor.py
import json
from bs4 import BeautifulSoup


def compress_page_source(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Drop non-visual / structural blocks completely
    for tag in soup(["script", "style", "meta", "link", "head", "noscript", "svg"]):
        tag.decompose()

    elements = []
    # Focus heavily on interactive or structural tags
    interactive_tags = {"a", "button", "input", "select", "textarea", "div", "span", "p", "h1", "h2", "h3"}

    for tag in soup.find_all(True):
        if tag.name not in interactive_tags:
            continue

        element = {"tag": tag.name}
        if tag.get("id"):
            element["id"] = tag["id"]
        if tag.get("class"):
            element["class"] = " ".join(tag["class"])
        if tag.get("name"):
            element["name"] = tag["name"]
        if tag.get("placeholder"):
            element["placeholder"] = tag["placeholder"]

        # Get only direct text strings belonging to this tag, skipping deep nested trees
        text = "".join([t for t in tag.find_all(text=True, recursive=False)]).strip()

        # Fallback to standard stripped string if it's a leaf node element (like a span/button)
        if not text and tag.name in ["a", "button", "span"] and tag.string:
            text = tag.string.strip()

        if text:
            # Keep reasonable length text but don't aggressively drop critical labels
            element["text"] = text[:120]

        # Only keep elements that have identifying attributes or text to keep JSON small
        if len(element) > 1:
            elements.append(element)

    return json.dumps(elements, indent=2)