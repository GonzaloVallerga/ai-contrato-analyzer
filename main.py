from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API viva!"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    doc = fitz.open(stream=contents, filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    truncated_text = text[:3000]  # Limitar para IA

    messages = [
        {"role": "system", "content": "Sos un abogado especializado en alquileres en Argentina."},
        {"role": "user", "content": f"Analizá este contrato y explicá si hay problemas o cláusulas injustas:\n\n{truncated_text}"}
    ]

    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "openchat/openchat-3.5",  # Podés usar otro modelo
        "messages": messages
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

    if response.status_code != 200:
        return {"error": "Fallo en OpenRouter", "details": response.text}

    result = response.json()
    ai_response = result["choices"][0]["message"]["content"]

    return {
        "extracted_text": truncated_text,
        "analysis": ai_response
    }
