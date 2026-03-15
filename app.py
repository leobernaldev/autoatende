from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversas = {}

SYSTEM_PROMPT = """Você é a assistente virtual da Clínica de Fisioterapia Bianca Bernal, localizada na Rua Alexandre Cheid, 216, São Paulo - SP.

Informações da clínica:
- Nome: Clínica Bianca Bernal
- Especialidades: Fisioterapia Ortopédica e Fisioterapia Neurológica
- Horário: Segunda a Sábado, das 8h às 20h
- Endereço: Rua Alexandre Cheid, 216 - São Paulo/SP

Sua função é:
- Responder dúvidas sobre os serviços da clínica
- Informar horários e endereço
- Ajudar pacientes a agendar consultas coletando nome, telefone e horário preferido
- Ser sempre educada, acolhedora e profissional

Quando alguém quiser agendar, colete: nome completo, telefone e horário de preferência, e diga que a equipe entrará em contato para confirmar."""

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