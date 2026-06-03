#!/usr/bin/env python3
"""
AI Cover Letter Generator — Usa OpenRouter/Gemini para generar cartas de presentación
Uso: python3 cover_letter_ai.py [job-title] [company] [role-type]

Role types: data-scientist | learning-analytics | ml-engineer | edtech-consultant
"""
import sys, os, json, requests

ROLE_PROFILES = {
    "data-scientist": "Data Scientist with 100+ end-to-end projects across finance, health, NLP, and computer vision. 3 Google certifications.",
    "learning-analytics": "Learning Analytics Specialist with B.A. in Educational Sciences, 11 years bridging pedagogy and data science.",
    "ml-engineer": "Machine Learning Engineer with expertise in NLP (Transformers, BERT), computer vision (CNN), and multiple LLM APIs.",
    "edtech-consultant": "EdTech consultant helping institutions leverage data for learning outcomes. 11 years of pedagogical experience."
}

def generate(job_title, company, role_type="data-scientist"):
    profile = ROLE_PROFILES.get(role_type, ROLE_PROFILES["data-scientist"])
    
    prompt = f"""Write a professional cover letter in English for the position of {job_title} at {company}.

Candidate profile:
- {profile}
- B.A. in Educational Sciences
- 3x Google Certified (Data Analytics, Advanced Data Analytics, Business Intelligence)
- 100+ data science projects on GitHub
- 11 years bridging education and technology since 2016
- Currently pursuing B.S. in Data Science for Business at UNRC
- Based in Tijuana, Mexico (open to remote)

Tone: Confident, professional, specific (cite actual achievements). 
Length: 3-4 paragraphs. 
Output ONLY the letter text, no explanations."""

    api_key = os.environ.get("MISTRAL_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("❌ No API key found. Set MISTRAL_API_KEY or OPENROUTER_API_KEY in ~/.env")
        return None

    # Try Mistral first (free tier available)
    try:
        response = requests.post(
            url="https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "temperature": 0.7,
            },
            timeout=30
        )
        if response.status_code != 200:
            raise Exception(f"Mistral failed: {response.status_code}")
    except:
        # Fallback to OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "google/gemma-4-31b-it",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 600,
            },
            timeout=30
        )
    
    if response.status_code == 200:
        letter = response.json()["choices"][0]["message"]["content"]
        filename = f"/tmp/opencode/Cover_Letter_{company}_{job_title}.txt"
        with open(filename, "w") as f:
            f.write(letter)
        print(f"✅ Cover letter saved: {filename}")
        print("\n" + "="*60)
        print(letter)
        print("="*60)
        return letter
    else:
        print(f"❌ Error: {response.status_code} - {response.text[:200]}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 cover_letter_ai.py [job-title] [company] [role-type]")
        print("Ej: python3 cover_letter_ai.py 'Data Scientist' 'Google' data-scientist")
        sys.exit(1)
    job_title = sys.argv[1]
    company = sys.argv[2]
    role_type = sys.argv[3] if len(sys.argv) > 3 else "data-scientist"
    generate(job_title, company, role_type)
