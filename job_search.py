#!/usr/bin/env python3
"""
Job Search Tool — Busca trabajos de Data Science/EdTech en plataformas públicas
Uso: python3 job_search.py [role] [location]

Roles: data-scientist | learning-analytics | ml-engineer | edtech-consultant | all
"""
import sys, json, requests, urllib.parse
from datetime import datetime

SEARCH_QUERIES = {
    "data-scientist": ["Data Scientist", "Data Analyst", "ML Engineer", "Data Science"],
    "learning-analytics": ["Learning Analytics", "Learning Engineer", "EdTech Analyst", "Instructional Data"],
    "ml-engineer": ["Machine Learning Engineer", "ML Ops", "AI Engineer", "NLP Engineer"],
    "edtech-consultant": ["EdTech Consultant", "Education Data", "Learning Consultant", "Academic Analytics"],
}

# Use GitHub Jobs API (free, no auth needed) + Adzuna free tier
def search_github_jobs(query, location=""):
    """Search GitHub Jobs (free API)"""
    results = []
    # GitHub Jobs API was deprecated, use alternative
    return results

def search_remotive(query):
    """Search Remotive API (free, no auth)"""
    try:
        url = f"https://remotive.com/api/remote-jobs?search={urllib.parse.quote(query)}&limit=10"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for job in data.get("jobs", []):
                results.append({
                    "title": job.get("title", ""),
                    "company": job.get("company_name", ""),
                    "url": job.get("url", ""),
                    "source": "Remotive",
                    "date": job.get("publication_date", "")[:10],
                })
        return results
    except:
        return []

def search_themuse(query):
    """Search The Muse API"""
    results = []
    try:
        url = f"https://www.themuse.com/api/public/jobs?category={urllib.parse.quote(query)}&page=1&descending=true"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for job in data.get("results", []):
                results.append({
                    "title": job.get("name", ""),
                    "company": job.get("company", {}).get("name", ""),
                    "url": f"https://www.themuse.com/jobs/{job.get('id', '')}",
                    "source": "The Muse",
                    "date": "",
                })
        return results
    except:
        return results

def main():
    role = sys.argv[1] if len(sys.argv) > 1 else "all"
    location = sys.argv[2] if len(sys.argv) > 2 else "remote"

    queries = []
    if role == "all":
        for qs in SEARCH_QUERIES.values():
            queries.extend(qs)
    else:
        queries = SEARCH_QUERIES.get(role, ["Data Scientist"])

    queries = list(set(queries))[:5]
    all_jobs = []

    for q in queries:
        all_jobs.extend(search_remotive(q))
        all_jobs.extend(search_themuse(q))

    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['title']}|{job['company']}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    # Sort by date
    unique_jobs.sort(key=lambda x: x["date"], reverse=True)

    print(f"\n{'='*60}")
    print(f"🔍 JOB SEARCH: {role.upper()} ({location})")
    print(f"{'='*60}")
    print(f"Found {len(unique_jobs)} positions\n")

    for i, job in enumerate(unique_jobs[:20], 1):
        print(f"{i:2d}. [{job['source']}] {job['title']}")
        print(f"    {job['company']}")
        print(f"    {job['url']}")
        if job["date"]:
            print(f"    Posted: {job['date']}")
        print()

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/tmp/opencode/jobs_{role}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(unique_jobs, f, indent=2)
    print(f"💾 Saved: {filename}")

if __name__ == "__main__":
    main()
