from django.db import models
from django.contrib.auth.models import User

class Resolution(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre de la résolution")
    question = models.TextField(verbose_name="Question (binaire)")
    context = models.TextField(verbose_name="Contexte", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Créée par")
    is_active = models.BooleanField(default=True, verbose_name="Active")

    def __str__(self):
        return self.title