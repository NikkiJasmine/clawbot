import os
import yaml
import openai
import requests
from bs4 import BeautifulSoup

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

MASTER_PROMPT = load_file("master_prompt.txt")
BASE_RESUME = load_file("base_resume.txt")
BASE_COVER = load_file("base_cover_letter.txt")

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def fetch_job_text(url):
    response = requests.get(url, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def run_clawbot(job_title, company, source, job_text):
    user_input = f"""
JOB SOURCE:
{source}

JOB TITLE:
{job_title}

COMPANY:
{company}

JOB DESCRIPTION:
{job_text}
"""

    messages = [
        {"role": "system", "content": MASTER_PROMPT},
        {"role": "user", "content": f"""
BASE RESUME:
{BASE_RESUME}

BASE COVER LETTER:
{BASE_COVER}

{user_input}
"""}
    ]

    response = openai.ChatCompletion.create(
        model=config["model"],
        messages=messages,
        temperature=config["temperature"],
        max_tokens=config["max_tokens"]
    )

    return response.choices[0].message["content"]

if __name__ == "__main__":
    print("Paste a job URL:")
    url = input().strip()

    print("Job title:")
    job_title = input().strip()

    print("Company name:")
    company = input().strip()

    print("Source (LinkedIn / Indeed / Company site):")
    source = input().strip()

    job_text = fetch_job_text(url)
    output = run_clawbot(job_title, company, source, job_text)

    filename = f"Application_{company}_{job_title}.txt".replace(" ", "_")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"✅ Generated: {filename}")
