from django.contrib import admin

from .models import Article, Storage


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'domain',
                    'add_date', 'pub_date', 'word_count')


class StorageAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'add_date')


# Models that listed in admin
admin.site.register(Article, ArticleAdmin)
admin.site.register(Storage, StorageAdmin)
