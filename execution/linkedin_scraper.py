import os
import json
import time
import logging
import shutil
import re
from dotenv import load_dotenv
from linkedin_api import Linkedin

# Configuração do sistema de logs automatizado em português brasileiro
log_file_path = os.path.join(".tmp", "aplicacao_scraper.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def save_to_tmp(filename, data):
    if not data or len(data) == 0:
        logging.warning(f"Atenção: Lista de dados vazia recebida! Ignorando o salvamento para preservar o arquivo {filename} existente.")
        return

    tmp_path = os.path.join(".tmp", filename)
    backup_path = os.path.join(".tmp", filename.replace(".json", "_backup.json"))
    
    if os.path.exists(tmp_path):
        try:
            shutil.copy2(tmp_path, backup_path)
        except Exception as e:
            logging.error(f"Erro ao criar arquivo de backup {backup_path}: {e}")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"Dados salvos com sucesso no caminho: {tmp_path}")

def get_linkedin_accounts():
    accounts = []
    # Tenta ler LINKEDIN_ACCOUNTS (formato email:senha,email2:senha2)
    acc_str = os.getenv('LINKEDIN_ACCOUNTS')
    if acc_str:
        for acc in acc_str.split(','):
            if ':' in acc:
                u, p = acc.split(':', 1)
                accounts.append((u.strip(), p.strip()))
    
    # Fallback para o modo antigo
    if not accounts:
        user = os.getenv('LINKEDIN_USER')
        pwd = os.getenv('LINKEDIN_PASS')
        if user and pwd:
            accounts.append((user, pwd))
            
    return accounts

def main():
    load_dotenv()
    
    accounts = get_linkedin_accounts()
    if not accounts:
        logging.error("Nenhuma conta do LinkedIn configurada no arquivo .env.")
        return

    api = None
    for user, pwd in accounts:
        try:
            logging.info(f"Iniciando processo de autenticação no LinkedIn com a conta: {user}...")
            api = Linkedin(user, pwd)
            # Teste simples para garantir que a API está respondendo e não retornou JSONDecodeError
            test_res = api.search_jobs('developer', limit=1)
            logging.info(f"Autenticação realizada com sucesso na conta: {user}!")
            break
        except Exception as e:
            logging.warning(f"Conta {user} falhou (limite atingido ou bloqueio). Tentando próxima...")
            api = None

    if not api:
        logging.error("Todas as contas configuradas falharam na autenticação. Verifique suas credenciais no arquivo .env.")
        return
        
    try:
        keywords = [
            "Webdesigner",
            "webdesign", 
            "Web designer", 
            "Web design",
            "Analista de suporte", 
            "Analista de Suporte (N1)",
            "Analista de Suporte N1",
            "Analista de Suporte (Atendimento)",
            "Assistente de Atendimento ao Cliente",
            "Assistente de Suporte",
            "Analista de atendimento"
        ]
        
        # Termos focados para capturar vagas divulgadas textualmente (Feed)
        feed_keywords = [
            "vaga 100% remota", 
            "home office", 
            "trabalho remoto", 
            "vaga remota"
        ]
        
        # Combinando todas as buscas
        todas_buscas = keywords + feed_keywords
        vagas_encontradas = []
        
        # Como o LinkedIn tem limites estritos, o ideal é fazer a busca com pausas.
        # Estamos criando a estrutura inicial para a busca das vagas e posts do feed.
        for kw in todas_buscas:
            logging.info(f"Iniciando varredura de vagas para o termo: '{kw}'...")
            
            try:
                from urllib.parse import urlencode
                import urllib.parse
                
                # Vamos buscar de 50 em 50 para não sobrecarregar
                for offset in range(0, 100, 50): # Limite de 100 por termo para evitar blocks e demorar demais
                    query_str = f"(origin:JOB_SEARCH_PAGE_QUERY_EXPANSION,keywords:{urllib.parse.quote(kw)},locationFallback:Brazil,selectedFilters:(workplaceType:List(2),timePostedRange:List(r86400)))"
                    params = {
                        "decorationId": "com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-174",
                        "count": 50,
                        "q": "jobSearch",
                        "query": query_str,
                        "start": offset,
                    }
                    res = api._fetch(
                        f"/voyagerJobsDashJobCards?{urlencode(params, safe='(),:')}",
                        headers={"accept": "application/vnd.linkedin.normalized+json+2.1"},
                    )
                    data = res.json()
                    elements = data.get("included", [])
                    
                    if not elements:
                        break
                        
                    # Mapear empresas para seus logos
                    companies = {}
                    for el in elements:
                        if el.get("$type") == "com.linkedin.voyager.dash.organization.Company":
                            urn = el.get("entityUrn")
                            try:
                                rootUrl = el["logo"]["vectorImage"]["rootUrl"]
                                artifact = el["logo"]["vectorImage"]["artifacts"][0]["fileIdentifyingUrlPathSegment"]
                                companies[urn] = rootUrl + artifact
                            except Exception:
                                pass

                    cards = [el for el in elements if el.get("$type") == "com.linkedin.voyager.dash.jobs.JobPostingCard"]
                    if not cards:
                        break
                        
                    logging.info(f"Foram encontradas {len(cards)} vagas (offset {offset}) para o termo '{kw}'.")
                    
                    for card in cards:
                        job_id = card.get("*jobPosting", "").split(":")[-1]
                        if not job_id:
                            continue
                            
                        titulo = card.get("jobPostingTitle", "")
                        if not titulo and "title" in card:
                            titulo = card["title"].get("text", "")
                            
                        empresa = (card.get("primaryDescription") or {}).get("text", "Não informada")
                        
                        # Ignorar spam e vagas sem empresa que poluem a tela e não tem logo
                        emp_lower = empresa.lower()
                        if "jobbol" in emp_lower or "não informada" in emp_lower or "não informado" in emp_lower or "página:" in emp_lower or "vagas remotas" in emp_lower or "nerdin" in emp_lower:
                            continue
                            
                        logo_urn = ""
                        try:
                            logo_urn = card["logo"]["attributes"][0]["detailData"]["*companyLogo"]
                        except Exception:
                            pass
                            
                        logo_url = companies.get(logo_urn, "")
                        
                        link_vaga = f"https://www.linkedin.com/jobs/view/{job_id}/"
                        salario = "Salário não informado"
                        
                        # Extrair quantidade de candidaturas das insights
                        candidaturas = "Não informado"
                        insight = (card.get("relevanceInsight") or {}).get("text", {})
                        if insight is None:
                            insight = {}
                        insight_text = insight.get("text", "")
                        
                        if "applicant" in insight_text.lower() or "candidatura" in insight_text.lower() or "clicaram" in insight_text.lower():
                            candidaturas = insight_text
                            
                        # Podemos usar secondaryDescription como resumo
                        descricao_resumida = (card.get("secondaryDescription") or {}).get("text", "Descrição detalhada disponível no link da vaga")
                        
                        vagas_encontradas.append({
                            "nome_empresa": empresa,
                            "logo_empresa": logo_url,
                            "titulo_vaga": titulo,
                            "descricao_resumida": descricao_resumida,
                            "salario": salario,
                            "link": link_vaga,
                            "candidaturas": candidaturas,
                            "termo_busca": kw,
                            "concorrencia": {
                                "comentarios": 0, 
                                "compartilhamentos": 0 
                            },
                            "detalhes": card
                        })
                    
                    # Salva em .tmp imediatamente após cada página
                    save_to_tmp("vagas_extraidas.json", vagas_encontradas)
                    time.sleep(2) # Pausa para evitar rate limit
                    
            except Exception as e:
                logging.error(f"Ocorreu um erro ao buscar o termo '{kw}': {e}")
                
            # --- SCRAPING DE POSTS (FEED) PARA O TERMO ---
            try:
                logging.info(f"Iniciando varredura no feed para publicações do termo: '{kw}'...")
                for offset in range(0, 100, 50):
                    params_posts = {
                        "count": 50,
                        "filters": "List(resultType->CONTENT)",
                        "keywords": kw,
                        "origin": "GLOBAL_SEARCH_HEADER",
                        "q": "all",
                        "start": offset
                    }
                    qs = urllib.parse.urlencode(params_posts, safe='(),->')
                    res_posts = api._fetch(
                        f"/search/blended?{qs}",
                        headers={"accept": "application/vnd.linkedin.normalized+json+2.1"},
                    )
                    data_posts = res_posts.json()
                    elements_posts = data_posts.get("included", [])
                    
                    posts = [el for el in elements_posts if el.get("$type") == "com.linkedin.voyager.dash.feed.Update"]
                    if not posts:
                        break
                        
                    logging.info(f"Encontrados {len(posts)} posts (offset {offset}) para o termo '{kw}'.")
                    
                    for post in posts:
                        post_str = json.dumps(post)
                        texts = re.findall(r'"text":\s*"([^"]+)"', post_str)
                        post_text = max(texts, key=len) if texts else ""
                        
                        if len(post_text) < 30:
                            continue
                            
                        post_urn = post.get("entityUrn", "")
                        link_post = f"https://www.linkedin.com/feed/update/{post_urn}/" if post_urn else "https://www.linkedin.com/"
                        
                        vagas_encontradas.append({
                            "nome_empresa": "Publicação no Feed",
                            "logo_empresa": "",
                            "titulo_vaga": f"Vaga via Post",
                            "descricao_resumida": post_text[:250] + "..." if len(post_text) > 250 else post_text,
                            "salario": "Tratar diretamente no post",
                            "link": link_post,
                            "candidaturas": "Veja no post",
                            "termo_busca": kw,
                            "concorrencia": {
                                "comentarios": 0, 
                                "compartilhamentos": 0 
                            },
                            "detalhes": {"full_text": post_text, "type": "feed_post"}
                        })
                        
                    save_to_tmp("vagas_extraidas.json", vagas_encontradas)
                    time.sleep(2)
            except Exception as e:
                logging.error(f"Erro ao buscar posts no feed para o termo '{kw}': {e}")
        
        # --- Buscando em Company Pages Específicas ---
        target_companies = ['home-office-vagas-remotas', 'nerdin', 'vagas-remotas-net']
        for company in target_companies:
            try:
                logging.info(f"Buscando posts da company page: {company}")
                updates = api.get_company_updates(company, max_results=30)
                if not updates:
                    continue
                
                for post in updates:
                    post_str = json.dumps(post)
                    # Extrair o texto principal do post usando regex simples
                    texts = re.findall(r'"text":\s*"([^"]+)"', post_str)
                    post_text = max(texts, key=len) if texts else ""
                    
                    # Remover quebras de linha escapadas para limpar o texto
                    post_text = post_text.replace('\\n', ' ').strip()
                    
                    if len(post_text) < 30:
                        continue
                        
                    urn = post.get("urn", "")
                    link_post = f"https://www.linkedin.com/feed/update/{urn}/" if urn else f"https://www.linkedin.com/company/{company}/posts/"
                    
                    vagas_encontradas.append({
                        "nome_empresa": f"Página: {company.replace('-', ' ').title()}",
                        "logo_empresa": "",
                        "titulo_vaga": f"Oportunidade via {company.title()}",
                        "descricao_resumida": post_text[:250] + "..." if len(post_text) > 250 else post_text,
                        "salario": "Acessar o post para detalhes",
                        "link": link_post,
                        "candidaturas": "Veja no post",
                        "termo_busca": "Grupos e Páginas",
                        "concorrencia": {
                            "comentarios": 0, 
                            "compartilhamentos": 0 
                        },
                        "detalhes": {"full_text": post_text, "type": "company_post"}
                    })
                time.sleep(2)
            except Exception as e:
                logging.error(f"Erro ao buscar posts da company {company}: {e}")
        
        # Ordenando por menor concorrência
        logging.info("Ordenando vagas capturadas pelo critério de menor concorrência...")
        vagas_encontradas.sort(key=lambda x: (x["concorrencia"]["comentarios"], x["concorrencia"]["compartilhamentos"]))
        
        # Salva em .tmp para o futuro app consumir
        save_to_tmp("vagas_extraidas.json", vagas_encontradas)
        logging.info("Processo finalizado com sucesso! Todas as vagas foram extraídas, unificadas e ordenadas.")
        
    except Exception as e:
        logging.critical(f"Erro fatal na execução do scraper: {e}")

if __name__ == "__main__":
    main()
