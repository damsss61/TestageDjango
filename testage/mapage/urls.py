from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('create-resolution/', views.create_resolution, name='create_resolution')
]