# Oportunidades - Sistema de Gestão e Scraping de Vagas

Um ecossistema completo para extração automatizada, gestão e notificação de vagas de emprego voltadas para o mercado de tecnologia. A aplicação busca ativamente oportunidades, aplica filtros de concorrência e apresenta uma interface moderna para que candidatos acompanhem o mercado.

---

## 🎯 O que o usuário pode fazer na plataforma?

A plataforma foi desenhada para ser o assistente definitivo na busca por vagas. Quando o usuário acessa o sistema, ele tem à sua disposição as seguintes funcionalidades:

1. **Painel de Vagas (Job Grid):** Visualizar vagas atualizadas em uma interface incrivelmente moderna (estilo Glassmorphism). As vagas trazem um resumo descritivo, quantidade de candidaturas concorrentes e a empresa contratante.
2. **Sistema de Contas:** O usuário pode se cadastrar e fazer login de forma totalmente segura para salvar o seu progresso na nuvem.
3. **Análise de Currículo Inteligente:** O usuário pode fazer o upload do seu currículo em PDF (ou até imagens JPG do currículo). O sistema fará a leitura e, sempre que o usuário ver as vagas, mostrará um **Score de Afinidade (%)** indicando o quão compatível o currículo dele é com aquela vaga específica.
4. **Integração Visual com LinkedIn:** O usuário pode fornecer a URL do seu perfil para vincular à conta, e gerenciar a remoção a qualquer momento.
5. **Assinatura de Newsletter Segmentada:** O usuário pode clicar no botão "Receber vagas por E-mail", escolher as áreas do seu interesse (ex: Web Design, Suporte e Atendimento, Vagas Gerais), e selecionar se quer receber e-mails 1x, 3x ou 5x ao dia.
6. **Formulário de Contato e Suporte:** Canal direto com a administração do sistema, equipado com filtros anti-spam invisíveis, para relatar bugs ou enviar sugestões.

---

## ⚙️ Como toda a aplicação funciona passo a passo?

A aplicação atua dividida em três pilares principais que operam sozinhos 24 horas por dia:

### 1. Motor de Busca (Web Scraper)
* O backend (em Python) possui uma rotina de *background jobs* operada pelo `apscheduler`. A cada 1 hora, de forma invisível, um robô acessa o LinkedIn e varre milhares de dados utilizando as credenciais de sistema.
* Ele busca não apenas vagas listadas nas páginas corporativas, mas varre a **Timeline (Feed)** atrás de publicações de pessoas e recrutadores dizendo coisas como *"Vaga 100% remota"* ou *"Estamos contratando"*.
* Após a extração, o script analisa a "concorrência" daquela vaga (número de likes, comentários, candidaturas no LinkedIn) e salva apenas as melhores no banco de dados temporário.

### 2. A Inteligência de Análise (Matching Engine)
* Quando o usuário sobe um currículo, o sistema não lê apenas texto. Se for uma imagem disfarçada de PDF, a engine de **OCR (Tesseract)** é acionada para extrair os caracteres contidos nas imagens.
* Todo o texto lido passa por um algoritmo matemático de *Machine Learning* chamado **TF-IDF (Term Frequency - Inverse Document Frequency)** cruzado com similaridade de cossenos. Isso significa que o sistema compara tecnicamente as palavras-chave exigidas na vaga com as palavras presentes na experiência do currículo, gerando o "Score" em porcentagem que o usuário visualiza na tela.

### 3. O Distribuidor (Newsletter e Notificações)
* O usuário que se cadastrou na Newsletter vai para um banco de dados inteligente isolado (`newsletter.db`).
* Nos horários estipulados (manhã, tarde, noite), o servidor lê todos os assinantes, agrupa as vagas mais quentes e menos concorridas baseando-se nas categorias escolhidas, e constrói dinamicamente um E-mail de notificação profissional em HTML. 
* O servidor dispara tudo via `SMTP`, com intervalos anti-spam automáticos. E cada e-mail traz o seu próprio token criptografado único, caso o usuário queira clicar no link seguro para se descadastrar com um clique.

---

## Tecnologias Utilizadas

### Backend
* **Python 3.x / Flask** (API RESTful)
* **SQLite** (Bancos de dados locais separados para usuários e newsletter)
* **APScheduler** (Agendador de tarefas assíncronas)
* **PyMuPDF / pytesseract** (Motor de OCR e manipulação de arquivos)
* **scikit-learn** (Cálculo de similaridade de texto vetorial via TF-IDF)

### Frontend
* **React** (Vite)
* **CSS Moderno / Glassmorphism** (UI/UX focada em alta usabilidade e estética Premium)

---

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
Este projeto é de uso educacional/demonstrativo. Desenvolvido com foco em arquitetura de dados limpa e melhores práticas de Engenharia de Software.
