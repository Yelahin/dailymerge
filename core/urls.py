from django.urls import path
from core.views import ArticleListView

urlpatterns = [
    path('category/<slug:slug>', ArticleListView.as_view(), name='filtered_news')
]