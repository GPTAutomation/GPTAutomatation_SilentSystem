# === SILENT SYSTEM BACKEND ===
# Module: search_scraper.py + generate_solution.py + product_launcher.py + index_page + auto_public_folder
# Purpose: Harvest pain points + generate AI-powered responses + deploy silent products + generate landing + move HTML to public folder

import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import openai
import os
import shutil

# --- CONFIG ---
HEADERS = {'User-Agent': 'Mozilla/5.0'}
SUBREDDITS = ["r/Entrepreneur", "r/freelance", "r/AItools", "r/startups"]
KEYWORDS = ["how do I", "any tools", "please help", "is there a way"]
OPENAI_API_KEY = "your-openai-key-here"
openai.api_key = OPENAI_API_KEY
PAYPAL_LINK = "https://paypal.me/GPTAutomation"
CONTACT_EMAIL = "GPTAutomation@proton.me"

# --- MODULE 1: PAIN POINT SCRAPER ---
def fetch_posts(subreddit):
    url = f"https://www.reddit.com/{subreddit}/hot.json?limit=20"
    try:
        res = requests.get(url, headers=HEADERS)
        posts = res.json()['data']['children']
        return [p['data'] for p in posts]
    except:
        return []

def extract_pain_points(posts):
    leads = []
    for post in posts:
        text = (post.get('title', '') + ' ' + post.get('selftext', '')).lower()
        if any(keyword in text for keyword in KEYWORDS):
            leads.append({
                "pain_point": post['title'],
                "details": post.get('selftext', '')[:250],
                "url": f"https://reddit.com{post['permalink']}",
                "timestamp": datetime.utcnow().isoformat(),
                "tags": [],
                "urgency": text.count('?') + text.count('!')
            })
    return leads

def save_leads(leads):
    with open("leads_raw.json", "a") as f:
        for lead in leads:
            json.dump(lead, f)
            f.write("\n")

# --- MODULE 2: GPT SOLUTION GENERATOR ---
def generate_solution(lead):
    prompt = f"""
    Given the user pain point: "{lead['pain_point']}"

    Create:
    1. A short product idea (Notion template or AI prompt)
    2. A one-line description
    3. A monetization suggestion (freemium, bundle, upsell)
    Return in JSON format.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

def process_all_leads():
    all_products = [
        {
            "pain_point": "How do I get freelance clients without a portfolio?",
            "solution": "{\n  \"product\": \"Freelancer Cold DM Generator\",\n  \"description\": \"An AI tool that writes custom cold messages for landing freelance gigs.\",\n  \"monetization\": \"Free version for 5 messages/day, upgrade for unlimited\"\n}",
            "created_at": "2025-06-21T12:00:00Z"
        },
        {
            "pain_point": "Any AI tools to make social media content faster?",
            "solution": "{\n  \"product\": \"AI Content Calendar Builder\",\n  \"description\": \"Create a full month of content ideas with captions using a few keywords.\",\n  \"monetization\": \"One-time $5 download or included in bundle\"\n}",
            "created_at": "2025-06-21T12:10:00Z"
        },
        {
            "pain_point": "Is there a quick way to build landing pages for digital products?",
            "solution": "{\n  \"product\": \"No-Code Landing Page AI\",\n  \"description\": \"Just describe your product and it generates a full landing page in seconds.\",\n  \"monetization\": \"Upsell for access to templates, forms, and hosting\"\n}",
            "created_at": "2025-06-21T12:20:00Z"
        }
    ]

    with open("ai_products.json", "w") as f:
        json.dump(all_products, f, indent=2)

# --- MODULE 3: PRODUCT PAGE GENERATOR ---
def launch_product_pages():
    if not os.path.exists("ai_products.json"):
        print("No AI product file found.")
        return

    with open("ai_products.json", "r") as f:
        products = json.load(f)

    if not os.path.exists("public"):
        os.makedirs("public")

    for i, product in enumerate(products):
        filename = f"product_{i+1}.html"
        filepath = os.path.join("public", filename)
        with open(filepath, "w") as f:
            f.write(f"""
                <html>
                <head><title>{product['pain_point']}</title></head>
                <body>
                    <h1>{product['pain_point']}</h1>
                    <pre>{product['solution']}</pre>
                    <p><strong>Contact:</strong> {CONTACT_EMAIL}</p>
                    <a href="{PAYPAL_LINK}" target="_blank">Buy Now via PayPal</a>
                </body>
                </html>
            """)
        print(f"Deployed: {filepath}")

    # --- MODULE 4: INDEX PAGE GENERATOR ---
    index_path = os.path.join("public", "index.html")
    with open(index_path, "w") as index:
        index.write("""
        <html>
        <head><title>AI Product Bundle</title></head>
        <body>
            <h1>🔥 Exclusive AI Productivity Toolkit 🔥</h1>
            <p>Access all tools in one discounted bundle.</p>
            <ul>
        """)
        for i, product in enumerate(products):
            index.write(f'<li><a href="product_{i+1}.html">{product["pain_point"]}</a></li>\n')
        index.write(f"""
            </ul>
            <br>
            <a href="{PAYPAL_LINK}" target="_blank">💰 Get the Full Bundle Now</a>
            <p><strong>Contact:</strong> {CONTACT_EMAIL}</p>
        </body>
        </html>
        """)
        print("Homepage created: public/index.html")

# --- MAIN ---
def main():
    # Skip scraping for this run; use pre-filled data
    # all_leads = []
    # for sub in SUBREDDITS:
    #     posts = fetch_posts(sub)
    #     leads = extract_pain_points(posts)
    #     all_leads.extend(leads)

    # save_leads(all_leads)
    process_all_leads()
    launch_product_pages()

if __name__ == "__main__":
    main()
