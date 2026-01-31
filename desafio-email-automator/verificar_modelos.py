import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERRO: Chave não encontrada no .env")
else:
    genai.configure(api_key=api_key)
    print(f"Verificando modelos para a chave: {api_key[:5]}...")
    
    try:
        print("\n--- MODELOS DISPONÍVEIS ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        print("---------------------------\n")
    except Exception as e:
        print(f"Erro ao listar modelos: {e}")