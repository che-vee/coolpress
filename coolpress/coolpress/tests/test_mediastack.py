import datetime
from django.test import TestCase

from django.contrib.auth.models import User

from press.mediastack_manager import serialize_from_mediastack, get_mediastack_posts
from press.models import CoolUser, Post, Category, PostStatus


class MediaStackImports(TestCase):

    def test_post_serialization(self):
        returned_json = {
            "author": "CNN Super Staff",
            "title": "This may be the big winner of the market crash",
            "description": "This may be the big winner of the market crash",
            "url": "http://rss.cnn.com/~r/rss/cnn_topstories/~3/KwE80_jkKo8/a-sa-dd-3",
            "source": "CNN",
            "image": "https://cdn.cnn.com/cnnnext/dam/assets/150325082152-social-gfx-cnn-logo-super-169.jpg",
            "category": "general",
            "language": "en",
            "country": "us",
            "published_at": "2020-07-17T23:35:06+00:00"
        }
        body = "This may be the big winner of the market crash\nsee more at: http://rss.cnn.com/~r/rss/cnn_topstories/~3/KwE80_jkKo8/a-sa-dd-3"
        user = User.objects.create(username='cnnsuperstaff', first_name='CNN',
                                   last_name='Super Staff')
        cu = CoolUser.objects.create(user=user)
        cat = Category.objects.create(label='General', slug='general')
        post_expected = Post(title="This may be the big winner of the market crash", body=body,
                             image_link="https://cdn.cnn.com/cnnnext/dam/assets/150325082152-social-gfx-cnn-logo-super-169.jpg",
                             status=PostStatus.PUBLISHED,
                             author=cu,
                             category=cat,
                             publish_date=datetime.datetime(2020, 7, 17, 23, 35, 6,
                                                            tzinfo=datetime.timezone.utc))
        actual_post = serialize_from_mediastack(returned_json)
        self.assertEqual(actual_post, post_expected)

    def test_get_media_posts(self):
        response_json = {
            "author": "Luke Plunkett",
            "title": "Expensive Cars Have DLC Now, And It's Taking The Piss",
            "description": "For a few years now some car companies have been experimenting with an idea ripped straight out of video games. Someone, somewhere figured that hey, if people are willing to pay for a game then spend more money inside the game they already bought then they might do the same for cars—a far more expensive and lucrative…Read more...",
            "url": "https://kotaku.com/mercedes-bmw-car-dlc-subscription-unlock-video-games-1849818834",
            "source": "kotaku",
            "image": None,
            "category": "general",
            "language": "en",
            "country": "us",
            "published_at": "2022-11-24T00:50:31+00:00"
        }
        post_expected = serialize_from_mediastack(response_json)
        posts = get_mediastack_posts(sources=['kotaku'], date=datetime.datetime(2022, 11, 24),
                                     languages=['en'], categories=['general'], countries=['us'],
                                     keywords=['DLC'])
        self.assertEqual(posts[0], post_expected)

    def test_get_media_posts_failing(self):
        posts = get_mediastack_posts(sources=['cnn'])
        self.assertTrue(len(posts) > 0)
