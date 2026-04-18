from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout

def accueil(request):
    return render(request, 'accueil.html')

def custom_logout(request):
    logout(request)
    messages.success(request, "Tu as été déconnecté avec succès.")
    return redirect('accueil')  # Redirige vers la page d'accueil