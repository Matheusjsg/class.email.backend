from fastapi import UploadFile
from io import BytesIO
import pdfplumber

def extract_text_from_file(file: UploadFile) -> str:
    if file.filename and file.filename.endswith(".txt"):
        content = file.file.read()
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")
    elif file.filename and file.filename.endswith(".pdf"):
        text = ""
        pdf_bytes = BytesIO(file.file.read())
        with pdfplumber.open(pdf_bytes) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    return ""
