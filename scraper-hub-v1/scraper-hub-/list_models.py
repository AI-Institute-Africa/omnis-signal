import google.generativeai as genai
from app.config import settings

def list_models():
    if not settings.GEMINI_API_KEY:
        print("No API Key")
        return
    
    genai.configure(api_key=settings.GEMINI_API_KEY)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model: {m.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
