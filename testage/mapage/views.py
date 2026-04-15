from django.shortcuts import render
from django.http import HttpResponse

def accueil(request):
    return render(request, 'accueil.html')