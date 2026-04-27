from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from .models import Resolution, Comment
from .forms import ResolutionForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.db import models


def accueil(request):
    # Récupère les résolutions actives, en excluant les brouillons des autres utilisateurs
    if request.user.is_authenticated:
        # Résolutions publiques (non-draft) + brouillons de l'utilisateur connecté
        resolutions = Resolution.objects.filter(
            models.Q(is_active=True),
            ~models.Q(status='draft') | models.Q(created_by=request.user, status='draft')
        ).order_by('-created_at')
    else:
        # Résolutions publiques (non-draft) pour les utilisateurs non connectés
        resolutions = Resolution.objects.filter(is_active=True).exclude(status='draft').order_by('-created_at')

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
            # Détermine l'action choisie par l'utilisateur
            action = request.POST.get('action')
            if action == 'draft':
                resolution.status = 'draft'  # Statut "En cours de création"
            elif action == 'publish':
                resolution.status = 'evaluation'  # Statut "En cours d'évaluation"
            resolution.save()
            return redirect('accueil')  # Redirige vers la page d'accueil après la création
    else:
        form = ResolutionForm(initial={'status': 'draft'})
    return render(request, 'create_resolution.html', {'form': form})

@login_required
def edit_resolution(request, resolution_id):
    # Récupère la résolution ou retourne une erreur 404 si introuvable
    resolution = get_object_or_404(Resolution, id=resolution_id, created_by=request.user)

    if request.method == 'POST':
        form = ResolutionForm(request.POST, instance=resolution)
        if form.is_valid():
            # Détermine l'action choisie par l'utilisateur
            action = request.POST.get('action')
            if action == 'draft':
                resolution.status = 'draft'  # Statut "En cours de création"
            elif action == 'publish':
                resolution.status = 'evaluation'  # Statut "En cours d'évaluation"
            form.save()
            return redirect('accueil')  # Redirige vers la page d'accueil après la modification
    else:
        form = ResolutionForm(instance=resolution)  # Pré-remplit le formulaire avec les données existantes

    return render(request, 'create_resolution.html', {'form': form, 'editing': True})

@login_required
def resolution_details(request, resolution_id):
    # Récupère la résolution ou retourne une erreur 404 si introuvable
    resolution = get_object_or_404(Resolution, id=resolution_id)

    # Vérifie si l'utilisateur a le droit de voir cette résolution
    if resolution.status == 'draft' and resolution.created_by != request.user:
        return render(request, 'mon_app/403.html', status=403)  # Accès interdit

    return render(request, 'resolution_details.html', {'resolution': resolution})

@login_required
def add_comment(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.resolution = resolution
            comment.author = request.user
            comment.save()
            return redirect('read_comments', resolution_id=resolution.id)  # Redirige vers la page de lecture des commentaires
    else:
        form = CommentForm()

    return render(request, 'add_comment.html', {'form': form, 'resolution': resolution})

@login_required
def read_comments(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id)
    comments = Comment.objects.filter(resolution=resolution).order_by('-created_at')
    return render(request, 'read_comments.html', {'resolution': resolution, 'comments': comments})