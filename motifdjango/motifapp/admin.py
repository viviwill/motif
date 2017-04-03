from django.contrib import admin
from datetime import date
from django.utils.translation import ugettext_lazy as _



from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'date_joined', 'last_login')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'domain',
                    'add_date', 'pub_date', 'word_count')


class StorageAdmin(admin.ModelAdmin):
    list_display = ('id', 'upvotes', 'user', 'article',
                    'public', 'add_date', "rating_c", 'short_summary')


class SocialprofileAdmin(admin.ModelAdmin):
    model = SocialProfile.follows.through


class InviteAdmin(admin.ModelAdmin):
    list_display = ('invite_code', 'invite_code_given', 'invite_username', 'used_date')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'url', 'message')


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'type', 'vote_value', 'activity_date')


# Models that listed in admin
admin.site.register(Article, ArticleAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(SocialProfile, SocialprofileAdmin)
admin.site.register(Invite, InviteAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Activity, ActivityAdmin)
