from django.contrib import admin

from .models import Question, Choice

# allow polls app to be edited in admin
admin.site.register(Question)
admin.site.register(Choice)
