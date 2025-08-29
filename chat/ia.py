import requests
import os
from threading import Lock


conversations = {}
conversations_lock = Lock()


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma3:1b"


def create_prompt(phone):
    base_dir = os.path.dirname(__file__)
    caminho_empresa = os.path.join(base_dir, '..', "utils", "empresa.txt")

    with open(caminho_empresa, "r", encoding="utf-8") as f:
        empresa_contexto = f.read()

    mensagens = [
        {
            "role": "system",
            "content": f"""Você é uma atendente virtual da clínica de estética chamada 'Duda'.

Responda **somente em português**, de forma **educada, profissional, amigável e direta**, como se estivesse conversando no WhatsApp com o cliente de telefone {phone}.

✅ Responda apenas com base nas informações da empresa.
✅ Responda responda com comprimentos e brincadeira desde que seja respeitosos.
❌ Não responda perguntas de proceidmentos ou negocios que não tenham relação com estética nossa.

Não de explicações longas. Seja objetiva e clara.

Aqui estão os dados da empresa para referência:
Não reposda pergunta que não tenham correlação com a estetica

{empresa_contexto}"""
        }
    ]
    return mensagens


def send_message(entrada_usuario, phone):
    with conversations_lock:
        if phone not in conversations:
            conversations[phone] = create_prompt(phone)

        conversations[phone].append({"role": "user", "content": entrada_usuario})

        payload = {
            "model": MODEL,
            "messages": conversations[phone],
            "stream": False,
            "temperature": 0.2, #0.6
            "num_predict": 10
        }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        resposta = response.json()["message"]["content"]
        with conversations_lock:
            conversations[phone].append({"role": "assistant", "content": resposta})

        return resposta
    except requests.exceptions.RequestException as e:
        print(f"[ERRO DE CONEXÃO] {e}")
        return """Desculpe, estou com problemas para responder agora.
        Tente novamente em instantes."""
