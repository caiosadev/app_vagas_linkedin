# Oportunidades - Sistema de Gestão e Scraping de Vagas

Um ecossistema completo para extração automatizada, gestão e notificação de vagas de emprego voltadas para o mercado de tecnologia. A aplicação busca ativamente oportunidades, aplica filtros de concorrência e apresenta uma interface moderna para que candidatos acompanhem o mercado.

## Tecnologias Utilizadas

### Backend
* **Python 3.x**
* **Flask** (API RESTful)
* **SQLite** (Bancos de dados locais separados para usuários e newsletter)
* **APScheduler** (Agendador de tarefas assíncronas para scrapers e envio de e-mails)
* **PyMuPDF / pytesseract** (Motor de OCR para extração de texto de currículos baseados em imagens)
* **scikit-learn** (Cálculo de similaridade entre o currículo e vagas via TF-IDF)

### Frontend
* **React** (Vite)
* **CSS Moderno / Glassmorphism** (UI/UX focada em alta usabilidade e estética Premium)

## Funcionalidades Principais

* **Scraping Automático:** Robô coleta constantemente novas vagas baseadas em termos técnicos e vagas remotas de Feed/Timeline.
* **Sistema de Newsletter (Cron):** Disparo automatizado de e-mails via SMTP com as top 5 vagas de menor concorrência, formatadas em um template HTML e filtradas pelas áreas de interesse escolhidas pelo usuário (1x, 3x ou 5x ao dia).
* **Análise Inteligente de Currículo:** O sistema lê currículos (em PDF ou imagem) do usuário logado e cruza os dados com a lista de vagas para exibir um `Score de Afinidade` em porcentagem baseada em métricas e análise vetorial de texto.
* **Módulo de Segurança:** Endpoints protegidos por **JWT Tokens**. Senhas salvas com hash seguro (`werkzeug.security`).
* **Proteção Anti-Spam (Honeypot):** Formulários possuem campos invisíveis que barram bots de realizarem inscrições automatizadas indevidas na newsletter.

## Como Executar Localmente

**Pré-requisitos:**
* Python >= 3.9
* Node.js >= 18.x

### 1. Preparando o Backend
```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure suas variáveis de ambiente copiando o modelo (se disponível)
# ou crie um arquivo .env na pasta raiz com SMTP_HOST, SMTP_USER, etc.

# Inicie o servidor
python execution/server.py
```
O servidor rodará na porta `5000`.

### 2. Preparando o Frontend
```bash
cd vagas-app

# Instale as dependências
npm install

# Inicie o ambiente de desenvolvimento
npm run dev
```
Acesse `http://localhost:5173`.

## Autorização e Licença
Este projeto é de uso educacional/demonstrativo. Contribuições são bem-vindas. Desenvolvido para apresentar conhecimentos plenos na criação de arquiteturas completas do frontend ao background jobs.
