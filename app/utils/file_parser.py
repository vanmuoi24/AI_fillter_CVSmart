from io import BytesIO
from typing import Dict, Any
from pypdf import PdfReader
from docx import Document
from fastapi import UploadFile
import requests


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts).strip()
    except Exception as e:
        raise ValueError(f"Lỗi đọc PDF: {str(e)}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        doc = Document(BytesIO(file_bytes))
        texts = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(texts).strip()
    except Exception as e:
        raise ValueError(f"Lỗi đọc DOCX: {str(e)}")


def extract_text_from_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        raise ValueError(f"Lỗi đọc TXT: {str(e)}")


def detect_scan_pdf(extracted_text: str, min_text_length: int = 30) -> bool:
    """
    Detect scan PDF cơ bản:
    - Nếu PDF extract ra quá ít text thì xem như scan PDF / image-based PDF
    """
    return len((extracted_text or "").strip()) < min_text_length


async def extract_text_from_upload(file: UploadFile) -> Dict[str, Any]:
    content = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(content)
        is_scan_pdf = detect_scan_pdf(text)
        return {
            "content": text,
            "source_type": "pdf_scan" if is_scan_pdf else "pdf_text",
            "is_scan_pdf": is_scan_pdf,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    if filename.endswith(".docx"):
        text = extract_text_from_docx(content)
        return {
            "content": text,
            "source_type": "docx",
            "is_scan_pdf": False,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    if filename.endswith(".txt"):
        text = extract_text_from_txt(content)
        return {
            "content": text,
            "source_type": "txt",
            "is_scan_pdf": False,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    raise ValueError("Chỉ hỗ trợ file .pdf, .docx, .txt")


def download_file_from_url(url: str) -> bytes:
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise ValueError(f"Không tải được file từ URL: {str(e)}")


def extract_text_from_url(url: str, filename: str = "") -> Dict[str, Any]:
    file_bytes = download_file_from_url(url)
    lower_name = filename.lower() if filename else url.lower()

    if ".pdf" in lower_name:
        text = extract_text_from_pdf(file_bytes)
        is_scan_pdf = detect_scan_pdf(text)
        return {
            "content": text,
            "source_type": "pdf_scan" if is_scan_pdf else "pdf_text",
            "is_scan_pdf": is_scan_pdf,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    if ".docx" in lower_name:
        text = extract_text_from_docx(file_bytes)
        return {
            "content": text,
            "source_type": "docx",
            "is_scan_pdf": False,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    if ".txt" in lower_name:
        text = extract_text_from_txt(file_bytes)
        return {
            "content": text,
            "source_type": "txt",
            "is_scan_pdf": False,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    raise ValueError("URL không phải file hỗ trợ (.pdf, .docx, .txt)")


def extract_text_from_local_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "rb") as f:
        content = f.read()

    lower_name = file_path.lower()

    if lower_name.endswith(".pdf"):
        text = extract_text_from_pdf(content)
        is_scan_pdf = detect_scan_pdf(text)
        return {
            "content": text,
            "source_type": "pdf_scan" if is_scan_pdf else "pdf_text",
            "is_scan_pdf": is_scan_pdf,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    if lower_name.endswith(".docx"):
        text = extract_text_from_docx(content)
        return {
            "content": text,
            "source_type": "docx",
            "is_scan_pdf": False,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    if lower_name.endswith(".txt"):
        text = extract_text_from_txt(content)
        return {
            "content": text,
            "source_type": "txt",
            "is_scan_pdf": False,
            "ocr_confidence": None,
            "ocr_text_length": len(text)
        }

    raise ValueError("Chỉ hỗ trợ file .pdf, .docx, .txt")