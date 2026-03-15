from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import os
import re

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
- Ajudar pacientes a agendar consultas
- Ser sempre educada, acolhedora e profissional

IMPORTANTE: Quando alguém quiser agendar, colete OBRIGATORIAMENTE estas 3 informações em sequência:
1. Nome completo
2. Telefone
3. Horário de preferência

Quando tiver coletado as 3 informações, responda EXATAMENTE neste formato:
AGENDAMENTO_CONFIRMADO|nome=NOME_AQUI|telefone=TELEFONE_AQUI|horario=HORARIO_AQUI

Depois disso diga que a equipe entrará em contato para confirmar."""

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
    
    agendamento = None
    if "AGENDAMENTO_CONFIRMADO" in resposta_texto:
        try:
            nome = re.search(r'nome=([^|]+)', resposta_texto).group(1)
            telefone = re.search(r'telefone=([^|]+)', resposta_texto).group(1)
            horario = re.search(r'horario=([^|\n]+)', resposta_texto).group(1)
            agendamento = {"nome": nome, "telefone": telefone, "horario": horario}
            resposta_texto = re.sub(r'AGENDAMENTO_CONFIRMADO\|[^\n]+', '', resposta_texto).strip()
        except:
            pass
    
    conversas[sessao_id].append({
        "role": "assistant",
        "content": resposta_texto
    })
    
    return jsonify({
        "resposta": resposta_texto,
        "agendamento": agendamento
    })

if __name__ == '__main__':
    app.run(debug=True)