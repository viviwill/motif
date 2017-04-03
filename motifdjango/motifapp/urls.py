from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'motifapp'
urlpatterns = [
    url(r'^$', views.DiscoverView.as_view(), name='index'),

    # register, login, logout
    url(r'^idea_of_motif/$', views.idea_of_motif, name='idea_of_motif'),
    url(r'^activity/$', views.activity, name='activity'),
    url(r'^upvote_summary/$', views.upvote_summary, name='upvote_summary'),
    url(r'^register/$', views.register_user, name='register'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    # url(r'^update_profile/$', views.update_profile, name='update_profile'),
    url(r'^feedback_submit/$', views.feedback_submit, name='feedback_submit'),

    # add article
    url(r'^article_add/$', views.article_add, name='article_add'),

    # individual article page / summary edit/delete
    url(r'^(?P<article_id>[0-9]+)/$', views.article_read, name='article_read'),
    url(r'^(?P<article_id>[0-9]+)/summary_edit/$', views.summary_edit, name='summary_edit'),
    url(r'^(?P<article_id>[0-9]+)/summary_delete/$', views.summary_delete, name='summary_delete'),
    url(r'^(?P<article_id>[0-9]+)/rating_edit/$', views.rating_edit, name='rating_edit'),
    url(r'^(?P<article_id>[0-9]+)/article_delete/$', views.article_delete, name='article_delete'),
    url(r'^(?P<article_id>[0-9]+)/article_public_edit/$', views.article_public_edit, name='article_public_edit'),
    url(r'^(?P<article_id>[0-9]+)/theme_edit/$', views.article_edit_theme, name='article_edit_theme'),
    url(r'^(?P<article_id>[0-9]+)/article_storage_edit/$', views.article_storage_edit, name='article_storage_edit'),


    # user article list view
    url(r'^user/(?P<slug>[\w.@+-]+)/saved/$', views.UserView.as_view(), name='user_view'),
    url(r'^user/(?P<slug>[\w.@+-]+)/profile/$', views.UserProfile.as_view(), name='user_profile'),
    url(r'^user/(?P<slug>[\w.@+-]+)/activity/$', views.UserProfile.as_view(), name='user_activity'),
    url(r'^user/(?P<slug>[\w.@+-]+)/following/$', views.UserProfile.as_view(), name='user_following'),
    url(r'^user/(?P<slug>[\w.@+-]+)/follower/$', views.UserProfile.as_view(), name='user_follower'),

    # testing page
    url(r'^testing/testing/$', views.testing_view, name='testing_view'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)