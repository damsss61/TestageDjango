from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from .models import Resolution, Comment, UserResolutionComment, Vote
from .forms import ResolutionForm, CommentForm, VoteForm
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count 

def accueil(request):
    # Récupère les résolutions actives, en excluant les brouillons des autres utilisateurs
    if request.user.is_authenticated:
        # Résolutions publiques (non-draft) + brouillons de l'utilisateur connecté
        resolutions = Resolution.objects.filter(
            models.Q(is_active=True),
            ~models.Q(status='draft') | models.Q(created_by=request.user, status='draft')
        ).order_by('-created_at')
        # Récupère les résolutions que l'utilisateur a commentées
        user_commented_resolutions = UserResolutionComment.objects.filter(
            user=request.user, has_commented=True
        ).values_list('resolution_id', flat=True)
    else:
        # Résolutions publiques (non-draft) pour les utilisateurs non connectés
        resolutions = Resolution.objects.filter(is_active=True).exclude(status='draft').order_by('-created_at')
        user_commented_resolutions = []

    return render(request, 'accueil.html', {
        'resolutions': resolutions,
        'user_commented_resolutions': user_commented_resolutions
    })

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
    user_opinions = Comment.objects.filter(author=request.user, resolution=resolution).order_by('-created_at')

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

    return render(request, 'add_comment.html', {
        'form': form,
        'resolution': resolution,
        'user_opinions': user_opinions
    })

@login_required
def delete_opinion(request, opinion_id):
    opinion = get_object_or_404(Comment, id=opinion_id, author=request.user)
    resolution_id = opinion.resolution.id
    opinion.delete()
    return redirect('add_comment', resolution_id=resolution_id)

@login_required
def read_comments(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id)
    comments = Comment.objects.filter(resolution=resolution).order_by('-created_at')
    return render(request, 'read_comments.html', {'resolution': resolution, 'comments': comments})

@login_required
def upvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Vérifie si l'utilisateur a déjà upvoté
    if request.user in comment.upvotes.all():
        comment.upvotes.remove(request.user)  # Retire le vote si déjà présent
    else:
        comment.upvotes.add(request.user)  # Ajoute le vote
        # Retire le downvote si l'utilisateur avait downvoté
        if request.user in comment.downvotes.all():
            comment.downvotes.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def downvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Vérifie si l'utilisateur a déjà downvoté
    if request.user in comment.downvotes.all():
        comment.downvotes.remove(request.user)  # Retire le vote si déjà présent
    else:
        comment.downvotes.add(request.user)  # Ajoute le vote
        # Retire l'upvote si l'utilisateur avait upvoté
        if request.user in comment.upvotes.all():
            comment.upvotes.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def resolution_summary(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id)

    # Vérifie que la résolution est en statut "voting"
    if resolution.status != 'voting':
        return render(request, '403.html', status=403)  # Accès interdit si la résolution n'est pas en vote

    return render(request, 'resolution_summary.html', {'resolution': resolution})

@login_required
def comments_summary(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id)

    # Vérifie que la résolution est en statut "voting"
    if resolution.status != 'voting':
        return render(request, '403.html', status=403)

    # Récupère les commentaires les plus upvotés
    top_comments = Comment.objects.filter(
        resolution=resolution
    ).annotate(
        upvote_count=Count('upvotes')  # Compte le nombre d'upvotes pour chaque commentaire
    ).order_by('-upvote_count')[:10]
    return render(request, 'comments_summary.html', {
        'resolution': resolution,
        'top_comments': top_comments
    })

@login_required
def submit_vote(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id)

    if resolution.status != 'voting':
        return render(request, '403.html', status=403)

    existing_vote = Vote.objects.filter(user=request.user, resolution=resolution).first()
    if existing_vote:
        return render(request, 'already_voted.html', {'resolution': resolution})

    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            vote = form.save(commit=False)
            vote.user = request.user
            vote.resolution = resolution
            vote.save()
            return redirect('vote_confirmation', resolution_id=resolution.id)
    else:
        form = VoteForm()

    return render(request, 'submit_vote.html', {
        'form': form,
        'resolution': resolution
    })

@login_required
def vote_confirmation(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id)
    return render(request, 'vote_confirmation.html', {'resolution': resolution})

@login_required
def vote_results(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id)

    if resolution.status != 'resolved':
        return render(request, 'mon_app/403.html', status=403)

    votes = Vote.objects.filter(resolution=resolution)

    # Ordre des jugements (du pire au meilleur)
    judgment_order = {
        'reject': 0,
        'bad': 1,
        'average': 2,
        'good': 3,
        'excellent': 4,
    }

    # Compte les votes pour chaque jugement (toutes options confondues)
    all_judgments = []
    for vote in votes:
        # On prend en compte les jugements pour "Pour" ET "Contre"
        all_judgments.append(vote.judgment_for)
        all_judgments.append(vote.judgment_against)

    # Calcule la note médiane globale
    def calculate_median(judgments):
        if not judgments:
            return None
        sorted_judgments = sorted(judgments, key=lambda x: judgment_order[x])
        n = len(sorted_judgments)
        return sorted_judgments[n // 2] if n % 2 == 1 else sorted_judgments[n // 2 - 1]

    global_median = calculate_median(all_judgments)

    # Compte les votes pour chaque jugement et chaque option (Pour/Contre)
    for_votes = {judgment: 0 for judgment in judgment_order}
    against_votes = {judgment: 0 for judgment in judgment_order}

    for vote in votes:
        for_votes[vote.judgment_for] += 1
        against_votes[vote.judgment_against] += 1

    # Détermine le gagnant en comparant les notes médianes de "Pour" et "Contre"
    median_for = calculate_median([vote.judgment_for for vote in votes])
    median_against = calculate_median([vote.judgment_against for vote in votes])

    if median_for is None and median_against is None:
        winner = "Aucun vote"
    elif median_for is None:
        winner = "Contre"
    elif median_against is None:
        winner = "Pour"
    elif judgment_order.get(median_for, 0) > judgment_order.get(median_against, 0):
        winner = "Pour"
    elif judgment_order.get(median_for, 0) < judgment_order.get(median_against, 0):
        winner = "Contre"
    else:
        winner = "Égalité"

    # Prépare les données pour le graphique empilé
    labels = ['Pour', 'Contre']
    datasets = []
    colors = {
        'reject': '#dc3545',      # Rouge
        'bad': '#fd7e14',         # Orange
        'average': '#ffc107',     # Jaune
        'good': '#198754',        # Vert
        'excellent': '#20c997',   # Vert clair
    }

    # Pour chaque jugement, crée un dataset avec les comptes pour "Pour" et "Contre"
    for judgment in judgment_order:
        datasets.append({
            'label': dict(Vote.JUDGMENTS)[judgment],
            'data': [for_votes[judgment], against_votes[judgment]],
            'backgroundColor': colors[judgment],
        })

    return render(request, 'vote_results.html', {
        'resolution': resolution,
        'global_median': global_median,  # Médiane globale
        'median_for': median_for,
        'median_against': median_against,
        'winner': winner,
        'labels': labels,
        'datasets': datasets,
        'judgment_order': judgment_order,
    })

@login_required
def publish_debate(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id, created_by=request.user)
    if resolution.status == 'draft':
        resolution.status = 'evaluation'
        resolution.save()
        # Ajoute un message de succès
        from django.contrib import messages
        messages.success(request, "Le débat a été publié avec succès !")
    return redirect('resolution_details', resolution_id=resolution.id)

@login_required
def start_voting(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id, created_by=request.user)
    if resolution.status == 'evaluation':
        resolution.status = 'voting'
        resolution.save()
        from django.contrib import messages
        messages.success(request, "Le vote a commencé !")
    return redirect('resolution_details', resolution_id=resolution.id)

@login_required
def close_voting(request, resolution_id):
    resolution = get_object_or_404(Resolution, id=resolution_id, created_by=request.user)
    if resolution.status == 'voting':
        resolution.status = 'resolved'
        resolution.save()
        from django.contrib import messages
        messages.success(request, "Le vote a été clôturé !")
    return redirect('vote_results', resolution_id=resolution.id)