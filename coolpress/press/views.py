import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from press.models import Category, Post, CoolUser
from press.forms import PostForm, CategoryForm


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


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'post_detail.html', {'post_obj': post})


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
