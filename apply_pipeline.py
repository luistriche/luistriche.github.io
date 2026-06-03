#!/usr/bin/env python3
"""
Sistema Fénix de Aplicación Automatizada
Pipeline completo: Leer vacante → Match → Generar CV + Carta → Guardar tracker

Uso:
  python3 apply_pipeline.py                          # Ver resumen
  python3 apply_pipeline.py match "descripción..."   # Match de una vacante
  python3 apply_pipeline.py prepare "titulo" "empresa" "descripción..."  # Preparar aplicación
  python3 apply_pipeline.py stats                    # Ver estadísticas del tracker
"""
import json, os, sys, requests, datetime, urllib.parse, re
from pathlib import Path

# ─── Config ───
BASE_DIR = Path.home() / ".config" / "fenix"
PROFILE_PATH = BASE_DIR / "profile.json"
TRACKER_PATH = BASE_DIR / "applications_tracker.csv"
JOBS_DB_PATH = BASE_DIR / "jobs_db.json"
OUTPUT_DIR = Path.home() / "Escritorio" / "Aplicaciones"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(BASE_DIR, exist_ok=True)

# ─── Cargar perfil ───
def load_profile():
    with open(PROFILE_PATH) as f:
        return json.load(f)

# ─── Cargar/Inicializar Jobs DB ───
def load_jobs_db():
    if JOBS_DB_PATH.exists():
        with open(JOBS_DB_PATH) as f:
            return json.load(f)
    return {"jobs": [], "last_updated": ""}

def save_jobs_db(db):
    db["last_updated"] = datetime.datetime.now().isoformat()
    with open(JOBS_DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

# ─── Inicializar Tracker ───
def init_tracker():
    if not TRACKER_PATH.exists():
        with open(TRACKER_PATH, "w") as f:
            f.write("date,company,title,role_match,cv_version,status,notes\n")
    return TRACKER_PATH

# ─── Matchmaking (similitud de coseno simple) ───
def match_job(description, profile):
    """
    Calcula match score (0-100) basado en los REQUISITOS DE LA VACANTE:
    - Extrae los requisitos de la descripción (skills, roles, domain)
    - Mide cuántos de esos requisitos están en nuestro perfil
    """
    desc_lower = description.lower()

    # Perfil como set de skills en lowercase
    profile_skills = set()
    for cat, skills in profile["technical_skills"].items():
        for s in skills:
            profile_skills.add(s.lower().replace("-", " ").replace("_", " "))
    for cert in profile["certifications"]:
        profile_skills.add(cert["name"].lower())
        for sk in cert["skills"]:
            profile_skills.add(sk.lower().replace("-", " ").replace("_", " "))
    for role in profile["target_roles"]:
        profile_skills.add(role.lower())

    # Palabras clave a buscar en la descripción
    search_terms = [
        "python", "sql", "r", "machine learning", "deep learning", "nlp",
        "natural language", "tensorflow", "pytorch", "scikit learn", "pandas",
        "numpy", "streamlit", "power bi", "tableau", "looker", "docker", "git",
        "linux", "aws", "gcp", "azure", "api", "etl", "fastapi",
        "statistics", "regression", "classification", "clustering",
        "time series", "forecasting", "a/b testing",
        "data analysis", "data visualization", "data cleaning",
        "data scientist", "data analyst", "ml engineer", "data engineer",
        "business intelligence", "analytics", "dashboard",
        "education", "learning", "edtech", "pedagogy", "teaching",
        "google", "certification", "certified",
        "bachelor", "degree", "licenciatura", "graduate",
        "english", "bilingual", "spanish",
        "research", "experiment", "communication",
    ]

    # Qué requisitos pide la vacante?
    job_requirements = []
    for term in search_terms:
        if term in desc_lower:
            job_requirements.append(term)

    if not job_requirements:
        return 50  # Neutral si no podemos determinar

    # De esos requisitos, cuáles tenemos?
    matches = 0
    for req in job_requirements:
        if req in profile_skills:
            matches += 1
        elif any(req in s for s in profile_skills):
            matches += 1

    score = round((matches / len(job_requirements)) * 100)
    return min(score, 100)

# ─── Generar CV para vacante específica ───
def generate_tailored_cv(title, company, description, profile):
    """Determina el mejor rol y genera CV"""
    # Determinar el mejor role match
    role_scores = {}
    for role in profile["technical_skills"]["ml_dl"]:
        if role.lower() in description.lower():
            role_scores["ml-engineer"] = role_scores.get("ml-engineer", 0) + 10
    for role in ["learning", "analytics", "education", "edtech"]:
        if role in description.lower():
            role_scores["learning-analytics"] = role_scores.get("learning-analytics", 0) + 10
    for role in ["data scientist", "data science", "machine learning"]:
        if role in description.lower():
            role_scores["data-scientist"] = role_scores.get("data-scientist", 0) + 10

    best_role = max(role_scores, key=role_scores.get) if role_scores else "data-scientist"

    # Generar CV
    import subprocess
    cv_path = OUTPUT_DIR / f"{company}_{title}_CV.pdf"
    r = subprocess.run(
        [sys.executable, str(Path.home() / "generate_cv.py"), best_role],
        capture_output=True, text=True
    )
    return best_role, cv_path

# ─── Generar Cover Letter AI ───
def generate_cover_letter(title, company, description, profile):
    """Usa API Mistral/OpenRouter para generar carta"""
    prompt = f"""Write a professional cover letter for {title} at {company}.

Job Description:
{description[:1000]}

Candidate Profile:
- {profile['headline']}
- {profile['bio']}
- 3x Google Certified
- 100+ data science projects
- 11 years experience

Tone: Confident, specific, professional. 3-4 paragraphs. ONLY the letter text."""

    api_key = os.environ.get("MISTRAL_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return "⚠️ No API key disponible. Carta no generada."

    try:
        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "temperature": 0.7,
            },
            timeout=20
        )
        if r.status_code == 200:
            letter = r.json()["choices"][0]["message"]["content"]
            path = OUTPUT_DIR / f"{company}_{title}_Cover_Letter.txt"
            with open(path, "w") as f:
                f.write(letter)
            return str(path)
        else:
            # Fallback OpenRouter
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "google/gemma-4-31b-it",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 600,
                    "temperature": 0.7,
                },
                timeout=20
            )
            if r.status_code == 200:
                letter = r.json()["choices"][0]["message"]["content"]
                path = OUTPUT_DIR / f"{company}_{title}_Cover_Letter.txt"
                with open(path, "w") as f:
                    f.write(letter)
                return str(path)
    except Exception as e:
        return f"⚠️ Error: {e}"

    return "⚠️ No se pudo generar la carta."

# ─── Registrar en tracker ───
def log_application(company, title, match_score, cv_version, status="prepared"):
    init_tracker()
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(TRACKER_PATH, "a") as f:
        f.write(f"{date},{company},{title},{match_score}%,{cv_version},{status},\n")
    print(f"📝 Logged: {company} - {title} ({match_score}% match)")

# ─── Stats ───
def show_stats():
    init_tracker()
    with open(TRACKER_PATH) as f:
        lines = f.readlines()[1:]  # Skip header
    total = len(lines)
    if total == 0:
        print("📊 No applications tracked yet.")
        return
    applied = sum(1 for l in lines if "applied" in l.lower())
    interviewed = sum(1 for l in lines if "interview" in l.lower())
    print(f"📊 Application Stats:")
    print(f"   Total prepared: {total}")
    print(f"   Actually applied: {applied}")
    print(f"   Interviews: {interviewed}")
    if applied > 0:
        print(f"   Conversion rate: {interviewed/applied*100:.1f}%")

# ─── Main ───
def main():
    profile = load_profile()

    if len(sys.argv) < 2:
        # Resumen
        print(f"╔══════════════════════════════════════╗")
        print(f"║  SISTEMA FÉNIX — Pipeline de Empleo  ║")
        print(f"╚══════════════════════════════════════╝")
        print(f"Perfil: {profile['headline']}")
        print(f"Certificaciones: {len(profile['certifications'])}")
        print(f"Proyectos: 100+")
        print(f"Experiencia: {profile['years_experience']} años")
        print(f"\nComandos:")
        print(f"  match \"descripción\"   → Score de compatibilidad")
        print(f"  prepare \"title\" \"company\" \"desc\" → Preparar aplicación completa")
        print(f"  stats                 → Ver estadísticas del tracker")
        return

    cmd = sys.argv[1]

    if cmd == "match":
        desc = sys.argv[2] if len(sys.argv) > 2 else ""
        score = match_job(desc, profile)
        print(f"\n🎯 Match Score: {score}%")
        if score >= 70:
            print("✅ RECOMENDADO: Aplica a esta vacante")
        elif score >= 50:
            print("⚠️ MATCH MEDIO: Considera ajustar CV")
        else:
            print("❌ MATCH BAJO: No recomendado")
        return

    if cmd == "prepare":
        if len(sys.argv) < 5:
            print("Uso: apply_pipeline.py prepare \"title\" \"company\" \"description\"")
            return
        title = sys.argv[2]
        company = sys.argv[3]
        desc = sys.argv[4]

        print(f"\n🎯 Preparando aplicación para {title} en {company}")
        print("=" * 50)

        # 1. Match
        score = match_job(desc, profile)
        print(f"📊 Match Score: {score}%")

        if score < 40:
            print("⚠️ Match bajo. ¿Seguro que quieres continuar?")
            cont = input("Continuar? (s/n): ")
            if cont.lower() != 's':
                print("Cancelado.")
                return

        # 2. Generar CV
        best_role, cv_path = generate_tailored_cv(title, company, desc, profile)
        print(f"📄 CV generado ({best_role}): {cv_path}")

        # 3. Generar Cover Letter
        letter_path = generate_cover_letter(title, company, desc, profile)
        print(f"✉️ Cover Letter: {letter_path}")

        # 4. Log
        log_application(company, title, score, best_role)

        print(f"\n✅ Aplicación lista en: {OUTPUT_DIR}")
        return

    if cmd == "stats":
        show_stats()
        return

    print(f"Comando desconocido: {cmd}")

if __name__ == "__main__":
    main()
