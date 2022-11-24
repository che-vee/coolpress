import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Max
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets
from rest_framework.viewsets import GenericViewSet

from press.models import Category, Post, CoolUser, Comment, PostStatus
from press.forms import PostForm, CategoryForm, CommentForm
from press.serializers import CategorySerializer, PostSerializer, AuthorSerializer
from press.stats_manager import comment_analyzer


def home(request):
    categories = Category.objects.all().annotate(p_count=Count('post'))
    posts = Post.objects.all()[:5]

    return render(request, 'home.html', {'cat_obj': categories, 'posts_list': posts})


def authors_list(request):
    objects = CoolUser.objects.all()

    return render(request, 'authors_list.html', {'author_obj': objects})


def render_a_post(post):
    return f'<div style="margin: 20px;padding-bottom: 10px;"><h2>{post.title}</h2><p style="color: gray;">{post.body}</p><p>{post.author.user.username}</p></div>'


def posts_list(request):
    objects = Post.objects.all()[:20]
    return render(request, 'posts_list.html', {'posts_list': objects})


def trending_posts_list(request):
    objects = Post.objects.annotate(c_count=Count('comment')) \
                  .annotate(latest_comment=Max('comment__creation_date')).filter(c_count__gte=5) \
                  .order_by('-c_count').order_by('-latest_comment')[:20]

    return render(request, 'trending_posts_list.html', {'trending_posts_list': objects})


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    data = request.POST or {'votes': 10}
    form = CommentForm(data)

    comments = post.comment_set.filter(status='PUBLISHED').order_by('-creation_date')
    comment_stats = comment_analyzer(comments).top(10)
    return render(request, 'post_detail.html', {'post_obj': post, 'comment_form': form, 'comments': comments, 'stats': comment_stats})


@login_required
def add_post_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    data = request.POST or {'votes': 10}
    form = CommentForm(data)
    if request.method == 'POST':
        if form.is_valid():
            votes = form.cleaned_data.get('votes')
            body = form.cleaned_data['body']
            Comment.objects.create(votes=votes, body=body, post=post, author=request.user.cooluser)
            return HttpResponseRedirect(reverse('posts-detail', kwargs={'post_id': post_id}))

    return render(request, 'comment_add.html', {'form': form, 'post': post})


@login_required
def post_update(request, post_id=None):
    post = None
    if post_id:
        post = get_object_or_404(Post, pk=post_id)
        if request.user != post.author.user:
            return HttpResponseBadRequest('Not allowed to change others posts')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            instance = form.save(commit=False)
            username = request.user.username
            instance.author = CoolUser.objects.get(user__username=username)
            instance.save()
            return HttpResponseRedirect(reverse('posts-detail', kwargs={'post_id': instance.id}))
    else:
        form = PostForm(instance=post)

    return render(request, 'post_update.html', {'form': form})


@login_required
def new_category(request):
    form = CategoryForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            label = form.cleaned_data.get('label')
            slug = form.cleaned_data.get('slug')
            Category.objects.create(label=label, slug=slug, created_by=request.user.cooluser)
            return HttpResponseRedirect(reverse('posts-list'))
    else:
        form = CategoryForm()
    return render(request, 'category_add.html', {'form': form})


def cu_detail(request, user_id):
    cu = CoolUser.objects.get(id=user_id)
    return render(request, 'cooluser_detail.html', {'object': cu})



class PostClassBasedListView(ListView):
    paginate_by = 20
    queryset = Post.objects.filter(status=PostStatus.PUBLISHED).order_by('-last_update')
    context_object_name = 'posts_list'
    template_name = 'posts_list.html'


class AuthorPosts(PostClassBasedListView):

    def get_queryset(self):
        queryset = super(AuthorPosts, self).get_queryset()
        username = get_object_or_404(User, username=self.kwargs['username'])
        user = User.objects.get(username=username)
        author = CoolUser.objects.get(user_id=user.id)
        return queryset.filter(author=author)



class ModelNonDeletableViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass


class CategoryViewSet(ModelNonDeletableViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user.cooluser


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Post.objects.all().filter(status=PostStatus.PUBLISHED) \
        .order_by('-creation_date')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.cooluser)


class AuthorsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CoolUser.objects.alias(posts=Count('post')).filter(posts__gte=1)
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]
