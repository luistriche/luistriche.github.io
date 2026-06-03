# 🤖 Automatizaciones Instaladas

## 1. 🛡️ API Security (CRÍTICO)
- Tus API keys fueron MOVIDAS de `.bashrc` a `~/.env` (permisos 600)
- `.bashrc` ahora hace `source ~/.env` — seguro y funcional
- **NUNCA** compartas `~/.env` ni lo subas a GitHub

## 2. 📄 Generador de CV Multi-rol
`python3 ~/generate_cv.py [rol]`
Roles: `data-scientist`, `learning-analytics`, `ml-engineer`, `edtech-consultant`
- Cada CV se adapta al puesto específico
- Los PDFs están en: `luistriche.github.io/Luis_Triche_CV_[rol].pdf`

## 3. 🤖 AI Cover Letter Generator
`source ~/.env && python3 ~/cover_letter_ai.py "Job Title" "Company" [rol]`
Ej: `python3 cover_letter_ai.py "Data Scientist" "Coursera" learning-analytics`
- Usa Mistral API (gratis) o OpenRouter como fallback
- Genera cartas personalizadas para cada postulación

## 4. 🔍 Job Search Tool
`python3 ~/job_search.py [rol] [ubicación]`
Busca empleos en Remotive y The Muse

## 5. 🌐 Portfolio Web
`luistriche.github.io` — CVs, proyectos, certificaciones

## 6. 📊 Dashboard CV Interactivo
`github.com/luistriche/cv-dashboard` — Para deploy en Streamlit Cloud
