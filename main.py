from fastapi import FastAPI, File, UploadFile
import pdfplumber

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API viva!"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # Leemos el contenido del archivo PDF subido
    contents = await file.read()

    # Abrimos pdfplumber con el stream del archivo
    with pdfplumber.open(file.file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Retornamos los primeros 1000 caracteres extraídos
    return {"extracted_text": text[:1000]}
