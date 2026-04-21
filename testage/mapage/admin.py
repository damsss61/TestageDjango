from django.contrib import admin
from .models import Resolution

@admin.register(Resolution)
class ResolutionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'question', 'context')