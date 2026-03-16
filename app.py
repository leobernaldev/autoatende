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
- As avaliações são TOTALMENTE GRATUITAS
- Sessões individuais e particulares, não aceitamos convênio (mas emitimos recibo para reembolso)
- Sessões de 30 ou 55 minutos dependendo do diagnóstico
- Todos os aparelhos já estão inclusos no valor da sessão
- Valores acessíveis com várias formas de pagamento
- Fornecemos atestado para paciente e acompanhante se necessário

Sua função é:
- Responder dúvidas sobre os serviços da clínica
- Informar horários e endereço
- Ajudar pacientes a agendar avaliação gratuita
- Ser sempre educada, acolhedora e profissional

IMPORTANTE: Quando alguém quiser agendar, colete estas informações em sequência:
1. Nome completo
2. Telefone
3. Diagnóstico médico ou queixa principal

Após coletar as 3 informações, mostre EXATAMENTE este texto:

"Vamos agendar uma avaliação! Mas antes deixa eu explicar como trabalhamos:

As sessões são individuais e particulares, atendemos um paciente por vez.
Não aceitamos convênio, mas se precisar emitimos recibo para solicitar reembolso no seu convênio.
Temos sessões de 30 min ou 55 min, varia de acordo com a necessidade e o diagnóstico do paciente.
Os aparelhos utilizados já são todos inclusos no valor da sessão.
Os valores oscilam de acordo com o diagnóstico e tempo de duração da sessão necessária.
Nossos valores são bem acessíveis e temos várias formas de pagamento.
As avaliações são totalmente gratuitas! Durante a avaliação já vemos o avanço da doença, explico os tratamentos e passo os valores finais.
Se necessário fornecemos atestado para o paciente e acompanhante.

Clique no botão abaixo para agendar sua avaliação gratuita pelo WhatsApp! 😊"

Depois responda EXATAMENTE neste formato numa linha separada:
AGENDAMENTO_CONFIRMADO|nome=NOME_AQUI|telefone=TELEFONE_AQUI|horario=A combinar|diagnostico=DIAGNOSTICO_AQUI"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/painel')
def painel():
    return render_template('painel.html')

@app.route('/vendas')
def vendas():
    return render_template('vendas.html')

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
            horario = re.search(r'horario=([^|]+)', resposta_texto).group(1)
            diagnostico = re.search(r'diagnostico=([^|\n]+)', resposta_texto).group(1)
            agendamento = {"nome": nome, "telefone": telefone, "horario": horario, "diagnostico": diagnostico}
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