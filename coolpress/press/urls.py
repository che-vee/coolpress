

from django.urls import path
from press import views

urlpatterns = [
    path('home/', views.home),
    path('posts/', views.posts_list, name='posts-list'),
    path('post_details/<int:post_id>', views.post_detail, name='posts-detail'),
    path('category/add/', views.new_category, name='new-category'),
    path('post/update/<int:post_id>', views.post_update, name='post-update'),
    path('post/add/', views.post_update, name='post-add'),
]