import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse


from press.models import Category, Post, CoolUser, Comment
from press.forms import PostForm, CategoryForm, CommentForm


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
    return render(request, 'post_detail.html', {'post_obj': post, 'comment_form': form, 'comments': comments})


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