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

    pdl_url = "https://api.peopledatalabs.com/v5/company/search"
    pdl_headers = {"Content-Type": "application/json","X-api-key": PDL_API_KEY}
#     body = {
#     "query": {
#         "location.country": {"value": location or "India"},
#         "keywords": {"value": industry or "Software"}
#     },
#     "size": 5
# }
    ES_QUERY = {
  "query": {
    "bool": {
      "must": [
        # {"term": {"tags": industry}},
        {"match": {"industry": "financial services" }},
        {"match": {"location.country": "united states"}}
      ]
    }
  }
}
    PARAMS = {
  'query': json.dumps(ES_QUERY),
  'size': 2,
  'pretty': True
}
    # print("🔍 PDL request body:", json.dumps(body, indent=2))
    # print("🔍 PDL headers:", pdl_headers,pdl_headers,PARAMS)

    try:
        # companies_response = requests.get(pdl_url,headers=pdl_headers,params=PARAMS)
        companies_response = {
    "status": 200,
    "data": [
        {
            "name": "BNY",
            "website": "bny.com",
            "size": "10001+",
            "founded": 1784,
            "location": {
                "name": "new york, new york, united states",
                "country": "united states"
            },
            "summary": "We help make money work for the world — managing it, moving it and keeping it safe.",
            "tags": ["banking", "investment services", "financial services"],
            "profiles": [
                "linkedin.com/company/bnyglobal",
                "facebook.com/bnymellon",
                "twitter.com/bnymellon"
            ]
        },
        {
            "name": "John Hancock",
            "website": "johnhancock.com",
            "size": "10001+",
            "founded": 1862,
            "location": {
                "name": "boston, massachusetts, united states",
                "country": "united states"
            },
            "summary": "At John Hancock, we help our customers live longer, healthier, better lives.",
            "tags": ["insurance", "retirement", "financial services"],
            "profiles": [
                "linkedin.com/company/john-hancock",
                "facebook.com/johnhancock",
                "twitter.com/johnhancockusa"
            ]
        }
    ]
}

        # print("🔁 PDL raw response text:", companies_response.text)
        # companies_response.raise_for_status()
        # companies_data = companies_response.json().get("data", [])
        companies_data = companies_response["data"]
    except requests.RequestException as e:
        logger.error(f"PDL API request failed: {e}")
        return Response({"error": "Failed to fetch companies from People Data Labs"}, status=502)

    saved_companies = []
    seen_domains = set()
    if not companies_data:
            logger.warning("✅ PDL responded but no companies found.")
    else:
            logger.info(f"✅ PDL returned {len(companies_data)} companies.")

    for company in companies_data:
        try:
            name = company.get("name")
            domain = company.get("website")
            size = company.get("size")
            founded = company.get("founded")
            location = company.get("location")
            print(f"➡️ Company: {name}, Domain: {domain}")
            if domain in seen_domains or not domain:
                continue
            seen_domains.add(domain)

            if not name or not domain:
                logger.warning("Skipping company with missing name/domain")
                continue

            # Hunter.io API
            try:
                hunter_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
                hunter_response = requests.get(hunter_url)
                hunter_response.raise_for_status()
                emails = hunter_response.json().get("data", {}).get("emails", [])
            except requests.RequestException as e:
                logger.warning(f"Hunter API failed for {domain}: {e}")
                emails = []

            # GNews API
            try:
                gnews_url = f"https://gnews.io/api/v4/search?q={name}&apikey={GNEWS_API_KEY}"
                gnews_response = requests.get(gnews_url)
                gnews_response.raise_for_status()
                news = gnews_response.json().get("articles", [])
                print("--------------------------")
                # print(news)
            except requests.RequestException as e:
                logger.warning(f"GNews API failed for {name}: {e}")
                news = []
                

            # OpenAI insights
            try:
                print("GROQ",name)
                openai_response = groq_insights(name, industry, location, size, news)
                if not openai_response:
                    logger.warning(f"OpenAI did not return insights for {name}")
                    continue
            except Exception as e:
                logger.warning(f"OpenAI failed for {name}: {e}")
                continue

            company_obj, _ = Company.objects.update_or_create(
    domain=domain,
    defaults={
        "name": name,
        "size": size,
        "location": location.get("name") if isinstance(location, dict) else location,
        "found_in": f"{founded}-01-01" if founded else None,
        "industry": industry,  # ✅ save the industry
        "description": openai_response.get("description", "No description available"),
        "pain_points": openai_response.get("pain_points", "Not provided"),
        "values": openai_response.get("values", "Not provided"),
        "services_suggestions": openai_response.get("services", "Not provided")
    }
)


            # Save contacts
            for email in emails:
                email_value = email.get("value")
                if not email_value:
                    continue
                Contact.objects.get_or_create(
                    company=company_obj,
                    email=email_value,
                    defaults={
                        "name": email.get("first_name", ""),
                        "phone": email.get("phone_number", ""),
                        "is_verified": email.get("verification", "") == "verified",
                        "designation": email.get("position", "")
                    }
                )

            # Save news
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

            # Save lead score
            LeadScore.objects.create(
                company=company_obj,
                score=openai_response["score"],
                reason="Based on OpenAI analysis"
            )

            saved_companies.append({
                "company": company_obj,
                "score": openai_response["score"]
                })

        except Exception as e:
            logger.error(f"Unexpected error processing company {company.get('name', '[unknown]')}: {e}")
            continue
    
    saved_companies.sort(key=lambda x: x["score"], reverse=True)
    companies_sorted = [c["company"] for c in saved_companies]
    serialized = CompanySerializer(companies_sorted, many=True)
    return Response(serialized.data)

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
        # print("🟢 GROQ raw content:", raw_content)

        # ✅ Extract JSON from noisy content
        json_data = extract_json_from_text(raw_content)
        # print("✅ Parsed JSON:", json_data)
        return json_data

    except Exception as e:
        # print("❌ Error in groq_insights:", e)
        return None


def extract_json_from_text(text):
    try:
        json_str = text[text.index("{"):]  # From first { to end
        return json.loads(json_str)
    except Exception as e:
        # print("❌ Failed to extract JSON:", e)
        return None
