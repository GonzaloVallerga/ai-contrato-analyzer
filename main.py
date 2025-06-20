import os
import httpx
from fastapi import FastAPI, File, UploadFile
import pdfplumber
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OPENROUTER_API_KEY = os.getenv(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)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def call_openrouter(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    with pdfplumber.open(file.file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    # Generar prompt para análisis:
    prompt = (
        "Analiza este contrato de alquiler para identificar cláusulas abusivas, "
        "recomendaciones y puntos de atención:\n\n" + text[:4000]  # limita texto para API
    )
    analysis = await call_openrouter(prompt)
    return {
        "extracted_text": text[:1000],
        "analysis": analysis
    }
