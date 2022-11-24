

from django.urls import path, include
from press import views
from press.views import AuthorPosts
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'authors', views.AuthorsViewSet)

urlpatterns = [
    path('home/', views.home, name='home'),
    path('posts/', views.posts_list, name='posts-list'),
    path('post_details/<int:post_id>', views.post_detail, name='posts-detail'),
    path('category/add/', views.new_category, name='new-category'),
    path('post/update/<int:post_id>', views.post_update, name='post-update'),
    path('post/<int:post_id>/comment-add/', views.add_post_comment, name='comment-add'),
    path('post/add/', views.post_update, name='post-add'),
    path('authors/', views.authors_list, name='authors-list'),
    path('trending/', views.trending_posts_list, name='trending-posts-list'),
    path('author/<int:user_id>', views.cu_detail, name='cooluser-detail'),
    path('posts/author/<str:username>', AuthorPosts.as_view(), name='author-posts'),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]