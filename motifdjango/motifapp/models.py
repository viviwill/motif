from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible


# Article model
@python_2_unicode_compatible
class Article(models.Model):
    title = models.TextField()
    author = models.TextField(null=True)
    domain = models.CharField(max_length=300, null=True)
    web_url = models.CharField(max_length=600, null=True)
    body_content = models.TextField()
    pub_date = models.DateTimeField('date published', null=True)
    add_date = models.DateTimeField('date added')
    word_count = models.IntegerField(null=True)

    def __str__(self):
        return '%s - %s' % (self.id, self.title)


# User following model
# Two col to link the user to their saved article
@python_2_unicode_compatible
class Storage(models.Model):
    user = models.ForeignKey(User)
    article = models.ForeignKey(Article)
    add_date = models.DateTimeField('date added', null=True)

    # todo check this field, see how to use blank and null
    # 2 ratings: creative and informative
    rating_c = models.IntegerField(blank=True, null=True)
    rating_i = models.IntegerField(blank=True, null=True)
    summary = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return '%s' % (self.article)


# User following model
