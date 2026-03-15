from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversas = {}

SYSTEM_PROMPT = """Você é um assistente virtual profissional e simpático chamado AutoAtende.
Você ajuda clientes de pequenas empresas respondendo dúvidas, agendando horários e dando informações.
Seja sempre educado, objetivo e útil.
Se não souber algo específico do negócio, diga que vai verificar com a equipe."""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    mensagem = data.get('mensagem')
    sessao_id = data.get('sessao_id', 'default')
    
    if sessao_id not in conversas:
        conversas[sessao_id] = []
    
    conversas[sessao_id].append({
        "role": "user",
        "content": mensagem
    })
    
    resposta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversas[sessao_id],
        max_tokens=1024
    )
    
    resposta_texto = resposta.choices[0].message.content
    
    conversas[sessao_id].append({
        "role": "assistant",
        "content": resposta_texto
    })
    
    return jsonify({"resposta": resposta_texto})

if __name__ == '__main__':
    app.run(debug=True)