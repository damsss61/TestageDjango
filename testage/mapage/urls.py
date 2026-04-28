from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('create-resolution/', views.create_resolution, name='create_resolution'),
    path('edit-resolution/<int:resolution_id>/', views.edit_resolution, name='edit_resolution'),
    path('resolution/<int:resolution_id>/', views.resolution_details, name='resolution_details'),
    path('resolution/<int:resolution_id>/add-comment/', views.add_comment, name='add_comment'),
    path('opinion/<int:opinion_id>/delete/', views.delete_opinion, name='delete_opinion'),
    path('resolution/<int:resolution_id>/comments/', views.read_comments, name='read_comments'),
    path('comment/<int:comment_id>/upvote/', views.upvote_comment, name='upvote_comment'),
    path('comment/<int:comment_id>/downvote/', views.downvote_comment, name='downvote_comment')
]