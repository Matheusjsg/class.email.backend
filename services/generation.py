import os, requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
GENERATION_MODEL = "google/flan-t5-base"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def generate_response_ai(text: str, categoria: str) -> str:
    prompt = f"O email abaixo foi classificado como '{categoria}'. Sugira uma resposta educada e profissional:\n\n{text}\n\nResposta:"
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{GENERATION_MODEL}",
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_new_tokens": 80}}
        )
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].strip()
        return f"Resposta sugerida para categoria '{categoria}'"
    except Exception as e:
        print("Erro na geração de resposta IA:", e)
        return f"Resposta sugerida para categoria '{categoria}'"
