from django.contrib import admin
from press.models import Category, Post, CoolUser


class CategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    list_filter = ['category']
    list_display = ['title', 'author']


admin.site.register(Post, PostAdmin)


class CoolUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(CoolUser, CoolUserAdmin)
