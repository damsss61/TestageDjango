from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from .models import Resolution
from .forms import ResolutionForm
from django.contrib.auth.decorators import login_required


def accueil(request):
    resolutions = Resolution.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'accueil.html', {'resolutions': resolutions})

def custom_logout(request):
    logout(request)
    messages.success(request, "Tu as été déconnecté avec succès.")
    return redirect('accueil')  # Redirige vers la page d'accueil

@login_required
def create_resolution(request):
    if request.method == 'POST':
        form = ResolutionForm(request.POST)
        if form.is_valid():
            resolution = form.save(commit=False)
            resolution.created_by = request.user  # Associe la résolution à l'utilisateur connecté
            resolution.save()
            return redirect('accueil')  # Redirige vers la page d'accueil après la création
    else:
        form = ResolutionForm()
    return render(request, 'create_resolution.html', {'form': form})