from django.urls import path
from . import views

urlpatterns = [
    path('process-resume/', views.process_uploaded_resume, name='process_resume'),
    path('evaluate-ats/', views.generate_ats_evaluation, name='evaluate_ats'),
    path('recommend/', views.recommend_jobs, name='recommend_jobs'),
    
    # Premium Chatbot Routes
    path('chat/', views.chatbot_interface, name='premium_chat'),         # Renders the UI
    path('api/chat/', views.ask_rag_chatbot, name='rag_chat_api'),       # Handles the AJAX
]