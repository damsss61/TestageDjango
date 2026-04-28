from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Resolution(models.Model):
    STATUS_CHOICES = [
        ('draft', 'En cours de création'),
        ('evaluation', 'En cours d\'évaluation'),
        ('voting', 'En cours de vote'),
        ('resolved', 'Résolue'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre de la résolution")
    question = models.TextField(verbose_name="Question (binaire)")
    context = models.TextField(verbose_name="Contexte", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créée par")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    resolution = models.ForeignKey(Resolution, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Contenu du commentaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    upvotes = models.ManyToManyField(User, related_name='upvoted_comments', blank=True)
    downvotes = models.ManyToManyField(User, related_name='downvoted_comments', blank=True)

    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.resolution.title}"
    
    def total_upvotes(self):
        return self.upvotes.count()

    def total_downvotes(self):
        return self.downvotes.count()
    
@receiver(post_save, sender=Comment)
def update_user_resolution_comment(sender, instance, created, **kwargs):
    if created:
        UserResolutionComment.objects.get_or_create(
            user=instance.author,
            resolution=instance.resolution,
            defaults={'has_commented': True}
        )
class UserResolutionComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resolution = models.ForeignKey(Resolution, on_delete=models.CASCADE)
    has_commented = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'resolution')  # Un utilisateur ne peut commenter qu'une fois par résolution

    def __str__(self):
        return f"{self.user.username} a commenté {self.resolution.title}"