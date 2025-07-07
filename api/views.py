from rest_framework import viewsets
from .models import Company, Contact, NewsArticle, LeadScore
from .serializers import CompanySerializer, ContactSerializer, NewsArticleSerializer, LeadScoreSerializer
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response

import os
import requests
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Environment Variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PDL_API_KEY = os.getenv("PDL_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('-last_updated')
    serializer_class = CompanySerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('email')
    serializer_class = ContactSerializer

class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all().order_by('-published_date')
    serializer_class = NewsArticleSerializer

class LeadScoreViewSet(viewsets.ModelViewSet):
    queryset = LeadScore.objects.all().order_by('-created_at')
    serializer_class = LeadScoreSerializer

@api_view(['GET'])
def scrape_companies(request):
    industry = request.GET.get("industry")
    location = request.GET.get("location")

    if not industry or not location:
        return Response({"error": "Missing required parameters: industry and location"}, status=400)

    saved_companies = []
    seen_domains = set()

    # === 1. Fetch companies from DB ===
    existing_companies = Company.objects.filter(industry__icontains=industry, location__icontains=location)
    print(f"🔁 Found {existing_companies.count()} existing companies.")

    for company_obj in existing_companies:
        domain = company_obj.domain
        seen_domains.add(domain)
        name = company_obj.name
        print(f"🔄 Updating existing company: {name} ({domain})")

        # -- Contacts
        try:
            hunter_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
            hunter_response = requests.get(hunter_url)
            hunter_response.raise_for_status()
            emails = hunter_response.json().get("data", {}).get("emails", [])
        except:
            emails = []

        for email in emails:
            email_value = email.get("value")
            if not email_value:
                continue
            designation = email.get("position") or ""
            Contact.objects.get_or_create(
                company=company_obj,
                email=email_value,
                defaults={
                    "name": email.get("first_name") or "",
                    "phone": email.get("phone_number") or "",
                    "is_verified": email.get("verification", "") == "verified",
                    "designation": email.get("position") or ""
                }
            )

        # -- News
        try:
            gnews_url = f"https://gnews.io/api/v4/search?q={name}&apikey={GNEWS_API_KEY}"
            gnews_response = requests.get(gnews_url)
            gnews_response.raise_for_status()
            news = gnews_response.json().get("articles", [])
        except:
            news = []

        for article in news:
            url = article.get("url")
            if not url:
                continue
            NewsArticle.objects.get_or_create(
                company=company_obj,
                url=url,
                defaults={
                    "title": article.get("title"),
                    "published_date": article.get("publishedAt"),
                    "summary": article.get("description", "")
                }
            )

        # -- OpenAI
        try:
            openai_response = groq_insights(name, industry, location, company_obj.size, news)
            ai_score = openai_response.get("score", 1) if openai_response else 1
            if openai_response:
                final_score, reason = calculate_combined_score(company_obj, emails, news, ai_score)
            else:
                final_score, reason = 1, "Fallback: OpenAI not available"

            if openai_response:
                company_obj.description = openai_response.get("description", "No description available")
                company_obj.pain_points = openai_response.get("pain_points", "Not provided")
                company_obj.values = openai_response.get("values", "Not provided")
                company_obj.services_suggestions = openai_response.get("services", "Not provided")
                company_obj.save()

            LeadScore.objects.create(
                company=company_obj,
                score=final_score,
                reason=reason
            )

            saved_companies.append({
                "company": company_obj,
                "score": final_score
            })

        except Exception as e:
            logger.warning(f"OpenAI failed for {name}: {e}")
            saved_companies.append({
                "company": company_obj,
                "score": final_score
            })

    # === 2. Fetch new companies from PDL ===
    print("🌐 Fetching additional companies from PDL...")

    try:
        pdl_url = "https://api.peopledatalabs.com/v5/company/search"
        pdl_headers = {"X-api-key": PDL_API_KEY}
        pdl_params = {
            "query": json.dumps({
                "bool": {
                    "must": [
                        {"match": {"industry": industry}},
                        {"match": {"location.country": location}}
                    ]
                }
            }),
            "size": 10, #---------------------------
            "pretty": True
        }

        pdl_response = requests.get(pdl_url, headers=pdl_headers, params=pdl_params)
        pdl_response.raise_for_status()
        companies_data = pdl_response.json().get("data", [])
        print(f"📦 PDL returned {len(companies_data)} companies.")

        for company in companies_data:
            domain = company.get("website")
            if not domain or domain in seen_domains:
                continue
            seen_domains.add(domain)

            name = company.get("name")
            size = company.get("size")
            founded = company.get("founded")
            location_name = company.get("location", {}).get("name")

            # -- Contacts
            try:
                hunter_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
                hunter_response = requests.get(hunter_url)
                hunter_response.raise_for_status()
                emails = hunter_response.json().get("data", {}).get("emails", [])
            except:
                emails = []

            # -- News
            try:
                gnews_url = f"https://gnews.io/api/v4/search?q={name}&apikey={GNEWS_API_KEY}"
                gnews_response = requests.get(gnews_url)
                gnews_response.raise_for_status()
                news = gnews_response.json().get("articles", [])
            except:
                news = []

            # -- OpenAI
            insights = groq_insights(name, industry, location, size, news)
            score = insights.get("score", 1) if insights else 1

            company_obj, _ = Company.objects.update_or_create(
                domain=domain,
                defaults={
                    "name": name,
                    "size": size,
                    "location": location_name,
                    "found_in": f"{founded}-01-01" if founded else None,
                    "industry": industry,
                    "description": insights.get("description", "No description available") if insights else "No description available",
                    "pain_points": insights.get("pain_points", "Not provided") if insights else "Not provided",
                    "values": insights.get("values", "Not provided") if insights else "Not provided",
                    "services_suggestions": insights.get("services", "Not provided") if insights else "Not provided"
                }
            )

            for email in emails:
                email_value = email.get("value")
                if not email_value:
                    continue
                Contact.objects.get_or_create(
                    company=company_obj,
                    email=email_value,
                    defaults={
                        "name": email.get("first_name") or "",
                        "phone": email.get("phone_number") or "",
                        "is_verified": email.get("verification", "") == "verified",
                        "designation": email.get("position", "")
                    }
                )

            for article in news:
                url = article.get("url")
                if not url:
                    continue
                NewsArticle.objects.get_or_create(
                    company=company_obj,
                    url=url,
                    defaults={
                        "title": article.get("title"),
                        "published_date": article.get("publishedAt"),
                        "summary": article.get("description", "")
                    }
                )

            LeadScore.objects.create(
                company=company_obj,
                score=score,
                reason="OpenAI analysis (PDL company)" if insights else "Fallback score (PDL)"
            )

            saved_companies.append({
                "company": company_obj,
                "score": score
            })

    except Exception as e:
        logger.error(f"PDL API error: {e}")


    # === 3. Final response ===
    if not saved_companies:
        return Response({"message": "No companies found or processed."}, status=204)

    saved_companies.sort(key=lambda x: x["score"], reverse=True)
    print(f"✅ Total companies returned to frontend: {len(saved_companies)}")
    response_data = []
    for entry in saved_companies:
        company_data = CompanySerializer(entry["company"]).data
        company_data["score"] = entry["score"]  # 🔥 attach the score to response
        response_data.append(company_data)
    return Response({"companies": response_data})

def groq_insights(name, industry, location, size, news_articles):
    import os, json, requests

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    news_snippets = "\n".join([
        f"{n.get('title', '')}: {n.get('description', '')}" for n in news_articles[:3]
    ])

    prompt = f"""
You are an intelligent business assistant. You will be provided with basic company details and recent news. Your job is to analyze the company and return insights in **pure JSON** format.

🛑 DO NOT add any explanation, introduction, commentary, or messages like "Here is the response". Only return the raw JSON.

🧠 CONTEXT:
Company Name: {name}
Industry: {industry}
Location: {location}
Size: {size}

Recent News (at most 3):
{news_snippets}

🎯 TASK:
Based on the information above, return a JSON object with the following keys:

- description: A professional and concise summary of the company.
- score: An integer from 1 to 5 representing the lead score. 1 = low potential, 5 = high potential.
- pain_points: List of business challenges the company is likely facing.
- values: The core values or priorities the company seems to uphold.
- services: 1–2 personalized service or product suggestions we could pitch.

✅ FORMAT (strictly follow this JSON schema):
{{
  "description": "...",
  "score": 1,
  "pain_points": ["...", "..."],
  "values": ["...", "..."],
  "services": ["...", "..."]
}}

Again, do NOT add anything outside this JSON. The response will be parsed programmatically.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        raw_content = data["choices"][0]["message"]["content"]
        return extract_json_from_text(raw_content)

    except Exception as e:
        return None

def extract_json_from_text(text):
    try:
        json_str = text[text.index("{"):]  # From first { to end
        return json.loads(json_str)
    except Exception as e:
        return None

def calculate_combined_score(company_obj, emails=None, news=None, ai_score=None):
    score = 0
    reasons = []

    if ai_score:
        score += ai_score
        reasons.append(f"LLM score: {ai_score}")

    # Contact Bonus
    if emails and len(emails) > 0:
        score += 1
        reasons.append(f"{len(emails)} emails found")

    # News Activity Bonus
    if news and len(news) >= 2:
        score += 1
        reasons.append(f"{len(news)} news articles found")

    # Size Bonus
    if company_obj.size and "10001+" in company_obj.size:
        score += 1
        reasons.append("Large company size")

    # Age Bonus
    if company_obj.found_in and company_obj.found_in.year < 2010:
        score += 1
        reasons.append("Company established before 2010")

    # Cap score at 5
    final_score = min(score, 5)
    return final_score, "; ".join(reasons)
