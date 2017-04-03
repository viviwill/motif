from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import truncatechars
from django.utils.encoding import python_2_unicode_compatible


# Article model
@python_2_unicode_compatible
class Article(models.Model):
    title = models.TextField()
    author = models.TextField(null=True)
    domain = models.CharField(max_length=300, null=True)
    web_url = models.CharField(max_length=600, null=True)
    lead_image_url = models.CharField(max_length=1000, null=True)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    add_date = models.DateTimeField('date added', null=True)

    # todo check this field, see how to use blank and null
    # 2 ratings: creative and informative
    rating_c = models.FloatField(blank=True, null=True)
    rating_i = models.FloatField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    summary_modified_date = models.DateTimeField('summary modified', blank=True, null=True)
    ratings_modified_date = models.DateTimeField('ratings modified', blank=True, null=True)
    public = models.BooleanField(default=True)

    # new since here
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return '%s: %s by %s' % (self.id, self.article.title, self.user)

    @property
    def short_summary(self):
        return truncatechars(self.summary, 30)

@python_2_unicode_compatible
class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    storage_interact = models.ForeignKey(Storage, on_delete=models.CASCADE)
    activity_date = models.DateTimeField(blank=True, null=True)
    vote_value = models.IntegerField(default=0)
    TYPE_CHOICES = (
        ('ADD', 'adds'),
        ('SAVE', 'saves'),
        ('UP', 'upvotes'),
        ('DOWN', 'downvotes'),
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=None,
    )

    def __str__(self):
        return '%s %s summary left by %s on %s' % \
               (self.user.username,
                self.get_type_display(),
                self.storage_interact.user,
                self.storage_interact.article.title)




# User following model
class SocialProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    user_portrait = models.ImageField(blank=True, upload_to='images/portrait')
    user_info = models.TextField(blank=True, null=True)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)
    theme_font_size = models.FloatField(default=1.4)
    theme_night_theme = models.BooleanField(default=False)

    def __str__(self):
        """Return human-readable representation"""
        return self.user.username


class Invite(models.Model):
    invite_code = models.CharField(max_length=50, null=True)
    invite_code_given = models.BooleanField(default=False)
    invite_username = models.CharField(max_length=50, null=True)
    used_date = models.DateTimeField('dated used', default=None)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

