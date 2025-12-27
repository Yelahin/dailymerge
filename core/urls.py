from django.urls import path
from core.views import news_page

urlpatterns = [
    path('', news_page, name='news')
]