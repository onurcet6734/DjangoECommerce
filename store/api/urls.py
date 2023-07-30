from django.urls import path
from . import views

urlpatterns = [
    path('indexAPI/', views.IndexApiView.as_view()),
]
