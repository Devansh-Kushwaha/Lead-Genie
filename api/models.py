from django.db import models

class Company (models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique= True)
    location=models.CharField(max_length=155, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    size=models.CharField(max_length=100,blank=True)
    found_in = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    pain_points = models.TextField(blank=True)
    values = models.TextField(blank=True)
    services_suggestions = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    
class Contact(models.Model):
    company=models.ForeignKey(Company,related_name='contacts', on_delete=models.CASCADE)
    name = models.CharField(max_length=255,blank=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=50,blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.email
    
class NewsArticle(models.Model):
    company = models.ForeignKey(Company, related_name='news_articles', on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    url=models.URLField()
    published_date=models.DateTimeField()
    summary=models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.title[:40]}..."
    
class LeadScore(models.Model):
    company = models.ForeignKey(Company, related_name='lead_scores', on_delete=models.CASCADE)
    score = models.IntegerField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__ (self):
        return f"{self.company.name} - Score: {self.score}"
    
    