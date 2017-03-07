from django.contrib import admin

from .models import *


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'domain',
                    'add_date', 'pub_date', 'word_count')


class StorageAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'add_date')


class SocialprofileAdmin(admin.ModelAdmin):
    model = SocialProfile.follows.through


# class FollowsInline(admin.TabularInline):
#     model = SocialProfile.follows.through
#
#
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('user', 'follows')
#     inlines = [FollowsInline, ]


# @admin.register(SocialprofileAdmin)
# class SocialFollow(admin.ModelAdmin):
#     inlines = (SocialprofileAdmin,)


# Models that listed in admin
admin.site.register(Article, ArticleAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(SocialProfile, SocialprofileAdmin)
