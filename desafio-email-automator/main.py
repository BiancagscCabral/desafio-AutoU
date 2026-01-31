import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import pypdf
import io

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("ERRO: A chave GEMINI_API_KEY não foi encontrada no arquivo .env")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

def clean_text(text: str) -> str:
    return " ".join(text.split())

@app.get("/")
def home():
    return {"message": "API de Classificação de Emails está ON! 🚀"}

@app.post("/analyze")
async def analyze_email(
    file: UploadFile = File(None), 
    text_input: str = Form(None)
):
    email_content = ""

    try:
        if file:
            if file.filename.endswith(".pdf"):
                pdf_reader = pypdf.PdfReader(file.file)
                for page in pdf_reader.pages:
                    email_content += page.extract_text() or ""
            elif file.filename.endswith(".txt"):
                content = await file.read()
                email_content = content.decode("utf-8")
            else:
                return {"error": "Formato não suportado. Use .pdf, .txt ou digite o texto."}
        elif text_input:
            email_content = text_input
        else:
            raise HTTPException(status_code=400, detail="Envie um arquivo ou texto.")

        if not email_content.strip():
            return {"error": "Não foi possível ler o conteúdo do email."}

        cleaned_content = clean_text(email_content)
        
        # --- AQUI ESTÁ A CORREÇÃO ---
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        prompt = f"""
        Você é um sistema de triagem de emails para uma empresa financeira.
        Analise o seguinte email:
        ---
        {cleaned_content}
        ---
        
        Tarefas:
        1. Classifique como "Produtivo" (requer ação, suporte, dúvidas) ou "Improdutivo" (spam, felicitações, irrelevante).
        2. Escreva uma resposta sugerida: formal, empática e curta.
        
        Saída OBRIGATÓRIA em JSON puro (sem markdown):
        {{
            "categoria": "Produtivo" ou "Improdutivo",
            "justificativa": "breve motivo",
            "resposta_sugerida": "texto da resposta"
        }}
        """

        response = model.generate_content(prompt)
        json_str = response.text.replace("```json", "").replace("```", "").strip()
        
        return {"result": json_str}

    except Exception as e:
        print(f"Erro no servidor: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)