from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import csv, os

from model.models import EmailText
from services.classification import classify_email_ai
from services.generation import generate_response_ai
from services.file_utils import extract_text_from_file

app = FastAPI()

FEEDBACK_FILE = "feedback/feedback.csv"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_email(email: EmailText):
    grupo, categoria, resposta = classify_email_ai(email.text)
    if resposta.startswith("Resposta sugerida para categoria"):
        resposta = generate_response_ai(email.text, categoria)
    return {"grupo": grupo, "categoria": categoria, "resposta": resposta}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    text = extract_text_from_file(file)
    if not text.strip():
        return {"erro": "Arquivo vazio ou formato não suportado"}
    grupo, categoria, resposta = classify_email_ai(text)
    if resposta.startswith("Resposta sugerida para categoria"):
        resposta = generate_response_ai(text, categoria)
    return {"grupo": grupo, "categoria": categoria, "resposta": resposta}

@app.post("/feedback")
async def feedback(
    email_text: str = Form(...),
    grupo: str = Form(...),
    categoria: str = Form(...),
    correto: bool = Form(...)
):
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([email_text, grupo, categoria, correto])
    return {"status": "ok"}
