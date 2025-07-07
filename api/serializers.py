from rest_framework import serializers
from .models import Company, Contact, NewsArticle, LeadScore

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'

class LeadScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadScore
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    news_articles = NewsArticleSerializer(many=True, read_only=True)
    lead_scores = LeadScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = '__all__'
