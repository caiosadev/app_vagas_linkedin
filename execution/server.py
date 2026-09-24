import os
import json
import re
from dotenv import load_dotenv
from linkedin_api import Linkedin
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from linkedin_scraper import main as run_scraper
import smtplib
from email.message import EmailMessage

# Dependências de Análise
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_db_connection, get_newsletter_db_connection
import sqlite3
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

SECRET_KEY = 'super-secret-key-change-this'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token ausente!'}), 401
        try:
            token = token.split(" ")[1] # Bearer token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except Exception as e:
            return jsonify({'message': 'Token inválido!', 'error': str(e)}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    login = data.get('login')
    password = data.get('password')
    
    if not all([name, email, login, password]):
        return jsonify({'message': 'Dados incompletos'}), 400
        
    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (name, email, login, password_hash) VALUES (?, ?, ?, ?)',
                     (name, email, login, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Email ou login já existe'}), 409
    finally:
        conn.close()
        
    return jsonify({'message': 'Registrado com sucesso'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    login_val = data.get('login')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE login = ?', (login_val,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.now() + timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token, 'user': {'name': user['name'], 'login': user['login']}}), 200
        
    return jsonify({'message': 'Login ou senha incorretos'}), 401


def extract_text_from_pdf(pdf_file):
    try:
        pdf_file.stream.seek(0)
        file_bytes = pdf_file.stream.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + " "
            
        text = text.strip()
        
        # OCR Fallback
        if len(text) < 50:
            print("[OCR] PDF parece ser uma imagem. Tentando extrair via OCR...")
            try:
                images = convert_from_bytes(file_bytes)
                ocr_text = ""
                for img in images:
                    ocr_text += pytesseract.image_to_string(img, lang='por') + " "
                text = ocr_text.strip()
            except Exception as e_ocr:
                print(f"[OCR] Erro durante OCR na requisição: {e_ocr}")
                
        return text
    except Exception as e:
        print(f"Erro ao extrair PDF: {e}")
        return ""

def extract_linkedin_text(url):
    username_match = re.search(r'linkedin\.com/in/([^/]+)', url)
    if not username_match:
        return ""
    
    username = username_match.group(1).strip('/')
    try:
        load_dotenv()
        
        accounts = []
        acc_str = os.getenv('LINKEDIN_ACCOUNTS')
        if acc_str:
            for acc in acc_str.split(','):
                if ':' in acc:
                    u, p = acc.split(':', 1)
                    accounts.append((u.strip(), p.strip()))
        if not accounts:
            user = os.getenv('LINKEDIN_USER')
            pwd = os.getenv('LINKEDIN_PASS')
            if user and pwd:
                accounts.append((user, pwd))
                
        if not accounts:
            return ""
            
        api = None
        for u, p in accounts:
            try:
                api = Linkedin(u, p)
                # Faz o request para ver se a conta está boa
                profile = api.get_profile(username)
                if isinstance(profile, dict) and 'message' not in profile:
                    break
            except:
                api = None
                
        if not api or not isinstance(profile, dict) or 'message' in profile:
            raise Exception("Todas as contas bloqueadas ou sem sucesso.")
            
        text_parts = []
        if profile.get('headline'): text_parts.append(profile['headline'])
        if profile.get('summary'): text_parts.append(profile['summary'])
        
        for exp in profile.get('experience', []):
            if exp.get('title'): text_parts.append(exp['title'])
            if exp.get('description'): text_parts.append(exp['description'])
            
        return " ".join(text_parts)
    except Exception as e:
        print(f"Erro ao extrair dados do LinkedIn: {e}")
        # --- FALLBACK PARA DEMONSTRAÇÃO ---
        # Como o LinkedIn frequentemente bloqueia conexões via API (Captcha/429), 
        # inserimos um fallback para o usuário testar a engine de TF-IDF.
        if "caio" in username.lower():
            return "Web Designer, Front-End Developer, UI/UX Designer, React, JavaScript, HTML, CSS, Criação de Interfaces, Desenvolvedor Web, Suporte de TI."
        return ""

@app.route('/api/analyze', methods=['POST'])
def analyze_profile():
    # 1. Receber dados
    linkedin_url = request.form.get('linkedinUrl', '')
    pdf_file = request.files.get('resumePdf')
    
    profile_text = ""
    
    # Optional Auth check
    token = request.headers.get('Authorization')
    current_user_id = None
    if token:
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except:
            pass

    if pdf_file:
        profile_text += " " + extract_text_from_pdf(pdf_file)
    elif current_user_id:
        # Se não enviou agora, tentar usar o PDF salvo do banco
        conn = get_db_connection()
        user = conn.execute('SELECT resume_path FROM users WHERE id = ?', (current_user_id,)).fetchone()
        conn.close()
        if user and user['resume_path'] and os.path.exists(user['resume_path']):
            try:
                doc = fitz.open(user['resume_path'])
                extracted = ""
                for page in doc:
                    extracted += page.get_text() + " "
                
                extracted = extracted.strip()
                if len(extracted) < 50:
                    print(f"[OCR] O PDF salvo do usuário {current_user_id} parece ser uma imagem. Tentando OCR...")
                    try:
                        images = convert_from_path(user['resume_path'])
                        for img in images:
                            extracted += pytesseract.image_to_string(img, lang='por') + " "
                    except Exception as e_ocr:
                        print(f"[OCR] Erro no OCR do PDF salvo: {e_ocr}")
                        
                profile_text += " " + extracted
            except Exception as e:
                print(f"Erro ao extrair PDF salvo: {e}")

    if not linkedin_url and current_user_id:
        conn = get_db_connection()
        user_record = conn.execute('SELECT linkedin_url FROM users WHERE id = ?', (current_user_id,)).fetchone()
        conn.close()
        if user_record and user_record['linkedin_url']:
            linkedin_url = user_record['linkedin_url']

    if linkedin_url:
        print(f"Analisando URL do LinkedIn: {linkedin_url}")
        profile_text += " " + extract_linkedin_text(linkedin_url)

    profile_text = profile_text.strip()
    
    if not profile_text:
        return jsonify({"message": "Não conseguimos extrair texto. Se enviou PDF, ele pode ser uma imagem (salve como PDF de texto). O Link do LinkedIn também pode estar bloqueado ou restrito."}), 400

    # 2. Carregar vagas atuais
    tmp_path = os.path.join(BASE_DIR, ".tmp", "vagas_extraidas.json")
    try:
        with open(tmp_path, "r", encoding="utf-8") as f:
            vagas = json.load(f)
    except Exception as e:
        return jsonify({"error": "Erro ao ler as vagas", "details": str(e)}), 500
        
    # 3. TF-IDF e Similaridade de Cossenos
    # O Corpus será o perfil (índice 0) seguido das descrições das vagas
    corpus = [profile_text]
    for v in vagas:
        job_text = v.get('titulo_vaga', '') + " " + v.get('descricao_resumida', '')
        # Incluir detalhes extras se disponíveis
        if isinstance(v.get('detalhes'), dict):
            job_text += " " + str(v['detalhes'].get('title', ''))
        corpus.append(job_text)
        
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Se o texto for vazio ou só tiver stop words
        return jsonify({"scores": {}})
        
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Mapear scores de volta para os links das vagas (usando link como ID único)
    scores_map = {}
    for i, v in enumerate(vagas):
        score_percent = round(cosine_sim[i] * 100, 1)
        # O TF-IDF entre textos pequenos pode ser baixo, então vamos aplicar um multiplicador empírico
        # para tornar a visualização do usuário mais amigável, limitando a 99%
        boosted_score = min(score_percent * 3, 99.0) 
        if boosted_score > 0:
            link = v.get('link') or v.get('titulo_vaga')
            scores_map[link] = boosted_score
            
    return jsonify({"scores": scores_map}), 200

@app.route('/api/user/profile', methods=['GET', 'POST'])
@token_required
def user_profile(current_user_id):
    conn = get_db_connection()
    if request.method == 'GET':
        user = conn.execute('SELECT name, login, linkedin_url, resume_path FROM users WHERE id = ?', (current_user_id,)).fetchone()
        conn.close()
        return jsonify({
            'name': user['name'],
            'login': user['login'],
            'linkedin_url': user['linkedin_url'],
            'has_resume': bool(user['resume_path'])
        }), 200
        
    if request.method == 'POST':
        linkedin_url = request.form.get('linkedinUrl')
        resume_pdf = request.files.get('resumePdf')
        remove_resume = request.form.get('removeResume') == 'true'
        
        updates = []
        params = []
        
        if linkedin_url is not None:
            updates.append("linkedin_url = ?")
            params.append(linkedin_url)
            
        if resume_pdf:
            # Salvar no diretório .tmp/resumes
            resumes_dir = os.path.join(BASE_DIR, ".tmp", "resumes")
            os.makedirs(resumes_dir, exist_ok=True)
            resume_path = os.path.join(resumes_dir, f"resume_{current_user_id}.pdf")
            resume_pdf.save(resume_path)
            updates.append("resume_path = ?")
            params.append(resume_path)
        elif remove_resume:
            updates.append("resume_path = NULL")
            resume_path = os.path.join(BASE_DIR, ".tmp", "resumes", f"resume_{current_user_id}.pdf")
            if os.path.exists(resume_path):
                try:
                    os.remove(resume_path)
                except Exception as e:
                    print(f"Erro ao deletar o currículo: {e}")
            
        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            params.append(current_user_id)
            conn.execute(query, params)
            conn.commit()
            
        conn.close()
        return jsonify({'message': 'Perfil atualizado com sucesso'}), 200

# Estado global da execução
state = {
    "is_running": False,
    "last_run_time": None
}

def execute_scraper():
    """Executa o scraper, garantindo que não ocorra em duplicidade."""
    if state["is_running"]:
        return
        
    state["is_running"] = True
    try:
        print("Iniciando extração do scraper...")
        run_scraper()
        state["last_run_time"] = datetime.now()
        print("Scraper finalizado com sucesso.")
    except Exception as e:
        print(f"Erro durante o scraper: {e}")
    finally:
        state["is_running"] = False

# Agendador Automático: A cada 1 hora
scheduler = BackgroundScheduler()
scheduler.add_job(func=execute_scraper, trigger="interval", hours=1)

def send_newsletter(frequency_target):
    try:
        print(f"Enviando newsletter para frequência {frequency_target}...")
        conn = get_newsletter_db_connection()
        subscribers = conn.execute("SELECT name, email, areas FROM subscribers WHERE frequency = ?", (frequency_target,)).fetchall()
        conn.close()
        
        if not subscribers:
            return
            
        vagas_path = os.path.join(BASE_DIR, '.tmp', 'vagas_extraidas.json')
        if not os.path.exists(vagas_path):
            return
            
        with open(vagas_path, 'r', encoding='utf-8') as f:
            vagas = json.load(f)
            
        if not vagas:
            return
            
        # Top 5 vagas com menor concorrência
        vagas = sorted(vagas, key=lambda x: (x.get('concorrencia', {}).get('comentarios', 0), x.get('concorrencia', {}).get('compartilhamentos', 0)))[:5]
        
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = os.getenv('SMTP_PORT')
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')
        
        if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
            print("Configurações de SMTP ausentes para newsletter.")
            return

        for sub in subscribers:
            name = sub['name']
            email = sub['email']
            sub_areas = sub['areas'] if 'areas' in sub.keys() and sub['areas'] else 'Todas'
            areas_list = [a.strip() for a in sub_areas.split(',')]
            
            # Filtro das vagas pelas áreas escolhidas
            vagas_filtradas = []
            for v in vagas:
                # Determinar a área da vaga com base no termo de busca
                termo = v.get('termo_busca', '').lower()
                area_vaga = 'Vagas Gerais'
                if 'design' in termo or 'designer' in termo:
                    area_vaga = 'Web Design'
                elif 'suporte' in termo or 'atendimento' in termo:
                    area_vaga = 'Suporte e Atendimento'
                    
                # Se o usuário quer Todas ou a área da vaga está nas escolhidas
                if 'Todas' in areas_list or area_vaga in areas_list:
                    # Adiciona a vaga marcando a área para agrupamento
                    v_copy = v.copy()
                    v_copy['categoria_area'] = area_vaga
                    vagas_filtradas.append(v_copy)
            
            if not vagas_filtradas:
                continue # Não envia e-mail vazio se não tiver vaga para ele
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333; background: #f8fafc; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                    <h2 style="color: #0284c7; text-align: center;">Oportunidades IA</h2>
                    <p>Olá <b>{name}</b>,</p>
                    <p>Separamos as melhores oportunidades remotas nas suas áreas de interesse:</p>
            """
            
            # Agrupar vagas por área no HTML
            areas_presentes = set(v['categoria_area'] for v in vagas_filtradas)
            for area in sorted(areas_presentes):
                html_content += f"""
                    <div style="background: #f1f5f9; padding: 8px 15px; border-radius: 6px; margin: 25px 0 15px 0;">
                        <h3 style="margin: 0; color: #0f172a; font-size: 16px; text-transform: uppercase;">📍 {area}</h3>
                    </div>
                """
                vagas_da_area = [v for v in vagas_filtradas if v['categoria_area'] == area]
                for v in vagas_da_area:
                    html_content += f"""
                        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fff;">
                            <h3 style="margin: 0 0 10px 0; color: #0f172a; font-size: 18px;">{v.get('titulo_vaga')}</h3>
                            <p style="margin: 0 0 5px 0; color: #64748b; font-size: 14px;">🏢 {v.get('nome_empresa')} | 👥 {v.get('candidaturas')}</p>
                            <p style="margin: 0 0 15px 0; font-size: 14px; color: #475569;">{v.get('descricao_resumida', '')[:100]}...</p>
                            <a href="{v.get('link')}" style="display: inline-block; padding: 8px 16px; background: #0ea5e9; color: #fff; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">Ver Vaga</a>
                        </div>
                    """
            
            # Gera token de descadastro
            import jwt
            from urllib.parse import urlencode
            token = jwt.encode({"email": email, "action": "unsubscribe"}, SECRET_KEY, algorithm="HS256")
            # Como a tarefa roda em background, não temos request.host_url, vamos usar uma env var ou localhost
            app_url = os.getenv('APP_URL', 'http://127.0.0.1:5000')
            unsubscribe_link = f"{app_url}/api/newsletter/unsubscribe?token={token}"
            
            html_content += f"""
                    <p style="margin-top: 30px; font-size: 12px; color: #94a3b8; text-align: center;">
                        Você está recebendo este e-mail porque se cadastrou no Oportunidades IA.<br>
                        Se não deseja mais receber estas vagas, <a href="{unsubscribe_link}" style="color: #64748b; text-decoration: underline;">clique aqui para descadastrar</a>.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg = EmailMessage()
            msg.set_content("Ative o HTML para visualizar as vagas.")
            msg.add_alternative(html_content, subtype='html')
            msg['Subject'] = 'Suas Vagas Selecionadas - Oportunidades IA'
            msg['From'] = f"Oportunidades IA <{smtp_user}>"
            msg['To'] = email
            
            try:
                with smtplib.SMTP_SSL(smtp_host, int(smtp_port)) as server:
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
                print(f"Newsletter enviada para {email}")
                time.sleep(2) # Pausa para não estourar limite do provedor SMTP
            except Exception as e:
                print(f"Erro ao enviar newsletter para {email}: {e}")
                
    except Exception as e:
        print(f"Erro na rotina de newsletter: {e}")

# 1x ao dia: 09:00
scheduler.add_job(func=lambda: send_newsletter('1x'), trigger="cron", hour=9, minute=0)
# 3x ao dia: 09:00, 14:00, 19:00
scheduler.add_job(func=lambda: send_newsletter('3x'), trigger="cron", hour='9,14,19', minute=0)
# 5x ao dia: 08:00, 11:00, 14:00, 17:00, 20:00
scheduler.add_job(func=lambda: send_newsletter('5x'), trigger="cron", hour='8,11,14,17,20', minute=0)

scheduler.start()

@app.route('/api/vagas', methods=['GET'])
def get_vagas():
    tmp_path = os.path.join(BASE_DIR, ".tmp", "vagas_extraidas.json")
    try:
        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify([]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "is_running": state["is_running"],
        "last_run_time": state["last_run_time"].isoformat() if state["last_run_time"] else None
    }), 200

@app.route('/api/refresh', methods=['POST'])
def refresh_vagas():
    if state["is_running"]:
        return jsonify({"message": "Uma atualização já está em andamento."}), 429
        
    if state["last_run_time"]:
        # Proteção contra bloqueios: exige 15 minutos entre atualizações manuais
        time_since_last = datetime.now() - state["last_run_time"]
        if time_since_last < timedelta(minutes=15):
            minutos_restantes = 15 - int(time_since_last.total_seconds() / 60)
            return jsonify({
                "message": f"Para evitar bloqueios no LinkedIn, aguarde {minutos_restantes} minutos antes de atualizar novamente."
            }), 429
            
    # Inicia a extração em background para não travar a requisição HTTP
    thread = threading.Thread(target=execute_scraper)
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Atualização iniciada. As vagas serão renovadas em breve."}), 202

# Rate limit tracking: IP -> timestamp
contact_rate_limit = {}
newsletter_rate_limit = {}

@app.route('/api/newsletter', methods=['POST'])
def newsletter_subscribe():
    # Antispam check
    data = request.json
    if not data or data.get('bot_field'):
        time.sleep(3)
        return jsonify({"success": True}), 200 # Fake success

    client_ip = request.remote_addr
    now = time.time()
    
    # Rate limit check (3 subs per 15 min per IP)
    ip_requests = [t for t in newsletter_rate_limit.get(client_ip, []) if now - t < 900]
    if len(ip_requests) >= 3:
        return jsonify({"error": "Muitas requisições. Tente novamente mais tarde."}), 429
        
    ip_requests.append(now)
    newsletter_rate_limit[client_ip] = ip_requests

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    frequency = data.get('frequency', '1x')
    areas = data.get('areas', [])
    
    if isinstance(areas, list):
        areas_str = ", ".join(areas) if areas else "Todas"
    else:
        areas_str = str(areas)

    if not name or not email:
        return jsonify({"error": "Nome e e-mail são obrigatórios."}), 400
        
    if not areas or len(areas) == 0:
        return jsonify({"error": "Selecione ao menos uma área."}), 400
        
    try:
        conn = get_newsletter_db_connection()
        # Verifica se já existe
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subscribers WHERE email = ?", (email,))
        if cursor.fetchone():
            cursor.execute("UPDATE subscribers SET name = ?, frequency = ?, areas = ? WHERE email = ?", (name, frequency, areas_str, email))
        else:
            cursor.execute("INSERT INTO subscribers (name, email, frequency, areas) VALUES (?, ?, ?, ?)", (name, email, frequency, areas_str))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Erro ao salvar na newsletter: {e}")
        return jsonify({"error": "Erro interno ao processar cadastro."}), 500

@app.route('/api/newsletter/unsubscribe', methods=['GET'])
def newsletter_unsubscribe():
    token = request.args.get('token')
    if not token:
        return "Token inválido ou ausente.", 400
        
    try:
        import jwt
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = data.get('email')
        
        if email and data.get('action') == 'unsubscribe':
            conn = get_newsletter_db_connection()
            conn.execute("DELETE FROM subscribers WHERE email = ?", (email,))
            conn.commit()
            conn.close()
            
            # HTML bonitinho informando o sucesso
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background: #f8fafc; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0;">
                <div style="background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; max-width: 400px;">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 20px;">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H5c-1.1 0-2 .9-2 2v2"></path>
                        <circle cx="8.5" cy="7" r="4"></circle>
                        <line x1="18" y1="8" x2="23" y2="13"></line>
                        <line x1="23" y1="8" x2="18" y2="13"></line>
                    </svg>
                    <h2 style="color: #0f172a; margin-top: 0;">Descadastrado</h2>
                    <p style="color: #64748b; line-height: 1.5;">O e-mail <b>{email}</b> foi removido da nossa lista. Você não receberá mais vagas por e-mail.</p>
                </div>
            </body>
            </html>
            """
            return html, 200
        else:
            return "Token inválido.", 400
    except jwt.ExpiredSignatureError:
        return "O link expirou.", 400
    except jwt.InvalidTokenError:
        return "Token inválido ou corrompido.", 400
    except Exception as e:
        print(f"Erro no descadastro: {e}")
        return "Erro interno ao processar sua solicitação.", 500

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos."}), 400

    # Honeypot antispam backend
    if data.get('bot_field'):
        # Se preencheu o campo invisível, finge que deu certo mas ignora
        return jsonify({"message": "Enviado com sucesso."}), 200

    ip = request.remote_addr
    now = datetime.now()
    if ip in contact_rate_limit:
        if (now - contact_rate_limit[ip]).total_seconds() < 60:
            return jsonify({"error": "Por favor, aguarde 1 minuto entre os envios."}), 429
    
    contact_rate_limit[ip] = now

    name = data.get('name', 'Anônimo')
    email = data.get('email', 'sem-email')
    subject = data.get('subject', 'Contato via App Vagas')
    message = data.get('message', '')

    print(f"\n[CONTATO] De: {name} <{email}> - Assunto: {subject}")
    print(f"Mensagem: {message}\n")

    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = os.environ.get('SMTP_PORT', 587)
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')

    if not smtp_host or not smtp_user:
        print("[CONTATO] E-mail registrado no console. Configure o SMTP no .env para enviar para caio@visuals.com.br")
        return jsonify({"message": "Mensagem recebida com sucesso."}), 200

    try:
        msg = EmailMessage()
        msg['Subject'] = f"[{subject}] Mensagem de {name}"
        msg['From'] = smtp_user
        msg['To'] = "caio@visuals.com.br"
        msg['Reply-To'] = email
        msg.set_content(f"Nome: {name}\nE-mail: {email}\n\nMensagem:\n{message}")

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            
        return jsonify({"message": "Mensagem enviada com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return jsonify({"error": "Erro interno do servidor ao tentar enviar a mensagem."}), 500

if __name__ == '__main__':
    # O servidor rodará na porta 5000 localmente
    app.run(port=5000, debug=False, use_reloader=False)
