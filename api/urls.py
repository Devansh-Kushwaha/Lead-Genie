from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import scrape_companies

router=DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'contacts', views.ContactViewSet)
router.register(r'news-articles', views.NewsArticleViewSet)
router.register(r'lead-scores', views.LeadScoreViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('scrape-companies/', scrape_companies),
]
