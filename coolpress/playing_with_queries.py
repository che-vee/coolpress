import os
import django
from django.db.models.functions import Length

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coolpress.settings")
django.setup()

from django.db.models import Count, Sum
from press.models import Post, CoolUser


def get_printed():
    authors = CoolUser.objects.annotate(characters=Sum(Length('post__body')) + Sum(Length('post__title')))
    for author in authors:
        total_characters = author.characters
        post_cnt = author.post_set.count()
        username = author.user.username

        print(f"{username}: {total_characters} characters on {post_cnt} posts.")


if __name__ == '__main__':
    get_printed()