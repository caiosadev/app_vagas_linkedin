import json

with open('.tmp/raw_dump.json', 'r') as f:
    elements = json.load(f)

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

vagas = []
for card in cards:
    job_id = card.get("*jobPosting", "").split(":")[-1]
    titulo = card.get("jobPostingTitle", "")
    empresa = (card.get("primaryDescription") or {}).get("text", "Não informada")
    logo_urn = ""
    try:
        logo_urn = card["logo"]["attributes"][0]["detailData"]["*companyLogo"]
    except Exception: pass
    logo_url = companies.get(logo_urn, "")
    link = f"https://www.linkedin.com/jobs/view/{job_id}/"
    insight_text = (card.get("relevanceInsight") or {}).get("text", {}).get("text", "")
    candidaturas = insight_text if any(x in insight_text.lower() for x in ["applicant", "candidatura", "clicaram"]) else "Não informado"
    
    vagas.append({
        "nome_empresa": empresa,
        "logo_empresa": logo_url,
        "titulo_vaga": titulo,
        "descricao_resumida": (card.get("secondaryDescription") or {}).get("text", "Remoto"),
        "salario": "Salário não informado",
        "link": link,
        "candidaturas": candidaturas,
        "termo_busca": "Restored Data",
        "concorrencia": {"comentarios": 0, "compartilhamentos": 0},
        "detalhes": card
    })

with open('.tmp/vagas_extraidas.json', 'w') as f:
    json.dump(vagas, f, ensure_ascii=False, indent=2)

print(f"Restored {len(vagas)} jobs")
