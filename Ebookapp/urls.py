from django.urls import path 
from . import views


urlpatterns = [
    path('BookConverter/', views.BookConverter.as_view()),
    path('BookText/', views.BookText.as_view()),
    path('DeleteBookText/', views.DeleteBookText.as_view()),

		]