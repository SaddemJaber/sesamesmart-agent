# tests/check_gemini_generation.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["GEMINI_API_KEY"]
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
HEADERS = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

def list_models():
    print("=== 1) LISTE DES MODELES ===")
    r = requests.get(f"{BASE_URL}/models", headers=HEADERS, timeout=30)
    print("Status:", r.status_code)
    r.raise_for_status()

    data = r.json()
    models = data.get("models", [])
    print("Nombre de modèles retournés :", len(models))

    flash_models = []
    for m in models:
        name = m.get("name", "")
        methods = m.get("supportedGenerationMethods", [])
        if "flash" in name.lower():
            flash_models.append((name, methods))

    if not flash_models:
        print("Aucun modèle 'flash' trouvé.")
    else:
        print("\nModèles flash trouvés :")
        for name, methods in flash_models:
            print(f"  - {name} | methods={methods}")

    return models

def pick_generation_model(models):
    """
    Priorité :
    1. un modèle contenant 'gemini-1.5-flash' + generateContent
    2. sinon n'importe quel modèle 'flash' + generateContent
    """
    for m in models:
        name = m.get("name", "")
        methods = m.get("supportedGenerationMethods", [])
        if "gemini-1.5-flash" in name and "generateContent" in methods:
            return name

    for m in models:
        name = m.get("name", "")
        methods = m.get("supportedGenerationMethods", [])
        if "flash" in name.lower() and "generateContent" in methods:
            return name

    return None

def test_generate(model_name):
    print("\n=== 2) TEST GENERATION ===")
    print("Modèle testé :", model_name)

    url = f"{BASE_URL}/{model_name}:generateContent"
    body = {
        "contents": [
            {
                "parts": [
                    {"text": "Réponds seulement par: OK"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 10
        }
    }

    r = requests.post(url, headers=HEADERS, json=body, timeout=30)
    print("Status:", r.status_code)

    try:
        data = r.json()
        print("Réponse JSON:")
        print(data)
    except Exception:
        print("Réponse brute:")
        print(r.text)

    r.raise_for_status()

if __name__ == "__main__":
    models = list_models()
    model_name = pick_generation_model(models)

    print("\n=== 3) MODELE CHOISI ===")
    print("Choisi :", model_name)

    if not model_name:
        raise RuntimeError("Aucun modèle compatible generateContent trouvé.")

    test_generate(model_name)