import re
import unicodedata


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFC", text)

    # Tách CamelCase: SoftwareEngineer -> Software Engineer
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    # Lowercase
    text = text.lower()

    # Tách chữ và số: python3 -> python 3
    text = re.sub(r"([a-z])([0-9])", r"\1 \2", text)
    text = re.sub(r"([0-9])([a-z])", r"\1 \2", text)

    # Giữ lại chữ, số, khoảng trắng
    text = re.sub(r"[^a-zA-ZÀ-ỹ0-9\s]", " ", text)

    # Xóa khoảng trắng thừa
    text = re.sub(r"\s+", " ", text).strip()

    return text


def is_english(text: str) -> bool:
    if not text:
        return False

    text = text.lower()

    english_markers = [
        "the", "and", "with", "for", "experience", "developer",
        "engineer", "requirements", "skills", "job", "backend"
    ]

    count = sum(1 for word in english_markers if word in text)
    return count >= 2