from django.contrib import admin

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'date_joined','last_login')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'domain',
                    'add_date', 'pub_date', 'word_count')


class StorageAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'add_date', "rating_c", 'summary')


class SocialprofileAdmin(admin.ModelAdmin):
    model = SocialProfile.follows.through


# Models that listed in admin
admin.site.register(Article, ArticleAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(SocialProfile, SocialprofileAdmin)
