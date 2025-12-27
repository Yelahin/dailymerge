from django.urls import path
from core.views import news_page

urlpatterns = [
    path('', news_page, name='news'),
    path('<slug:slug>', news_page, name='filtered_news')
]