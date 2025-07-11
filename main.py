import os
import httpx
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Leer API key de variable de entorno
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def call_openrouter(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://tuapp.com",  # Podés dejarlo así o usar tu dominio
        "X-Title": "ContratoAnalyzer"
    }
    json_data = {
        "model": "openai/gpt-3.5-turbo",  # ✅ MODELO GRATUITO
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        with pdfplumber.open(file.file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"

        prompt = (
            "Analizá este contrato de alquiler. Señalá cualquier cláusula abusiva, riesgosa o ambigua. "
            "Dá recomendaciones legales breves para mejorarlo:\n\n" + text[:4000]
        )

        analysis = await call_openrouter(prompt)

        return {
            "extracted_text": text[:1000],
            "analysis": analysis
        }

    except Exception as e:
        return {"error": str(e)}

