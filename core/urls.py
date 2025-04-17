from django.urls import path
from . import views
from .views import chat_with_deepseek
from .views import chat_api


urlpatterns = [
    path('', views.index, name='index'),
   # ✅ Use this for your JS-based chat API
    path('chat/', views.chat_api, name='chat_api'),
    path('chat/', views.chat_with_deepseek, name='chat'),

    # path('api/chat/', views.chat_api, name='chat_api'),

]
