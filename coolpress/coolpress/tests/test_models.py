from django.test import TestCase, Client

from django.contrib.auth.models import User
from django.urls import reverse

from press.models import Category, Post, CoolUser, PostStatus, Comment, CommentStatus


class PostModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='oscar')
        cu = CoolUser.objects.create(user=user)
        post = Post.objects.create(category=Category.objects.create(label='Tech', slug='tech'),
                                   title='a new mac is out there',
                                   author=cu)
        cls.user = user
        cls.post = post
        cls.cu = cu

    def test_checking_post_representation(self):
        actual = str(self.post)

        expected = f'a new mac is out there'
        self.assertEqual(actual, expected)

    def test_creation_proper_post(self):
        self.assertEqual(self.post.status, PostStatus.DRAFT)
        username = self.post.author.user.username
        self.assertIsNotNone(username)


class CommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='oscar')
        cu = CoolUser.objects.create(user=user)
        post = Post.objects.create(category=Category.objects.create(label='Tech', slug='tech'),
                                   title='a new mac is out there',
                                   author=cu)
        comment = Comment.objects.create(body='This is a test comment', votes=10, author=cu, post=post)

        cls.user = user
        cls.post = post
        cls.cu = cu
        cls.comment = comment

    def test_creation_proper_comment(self):
        self.assertTrue(isinstance(self.comment, Comment))
        self.assertEqual(self.comment.status, CommentStatus.PUBLISHED)

    def test_post_detail(self):
        response = self.client.get(reverse('posts-detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['comments']), 1)

    def test_post_detail_change_comment(self):
        self.comment.status = CommentStatus.NON_PUBLISHED
        self.assertEqual(self.comment.status, CommentStatus.NON_PUBLISHED)
        response = self.client.get(reverse('posts-detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(len(response.context['comments']), 0)


class TrendingPostModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='oscar')
        cu = CoolUser.objects.create(user=user)
        post = Post.objects.create(category=Category.objects.create(label='Tech', slug='tech'),
                                   title='a new mac is out there',
                                   author=cu)

        cls.user = user
        cls.post = post
        cls.cu = cu

    def test_creation_proper_post(self):
        self.assertTrue(isinstance(self.post, Post))

    def test_trending_post_none(self):
        response = self.client.get(reverse('trending-posts-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['trending_posts_list']), 0)

    def test_trending_post(self):
        comments = ['One', 'Two', 'Three', 'Four', 'Five']
        for comment in comments:
            Comment.objects.create(body=comment, votes=10, author=self.cu, post=self.post)
        response = self.client.get(reverse('trending-posts-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['trending_posts_list']), 1)
