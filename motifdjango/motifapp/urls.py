from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'motifapp'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    # register, login, logout
    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^profile/(?P<slug>[\w.@+-]+)/$', views.UserProfile.as_view(), name='user_profile'),

    # diffeent views
    url(r'^discover/$', views.DiscoverView.as_view(), name='discover'),
    url(r'^discover/(?P<article_id>[0-9]+)/$', views.article_read, name='article_read'),
    url(r'^discover/(?P<article_id>[0-9]+)/theme_edit/$', views.article_edit_theme, name='article_edit_theme'),

    # individual article page
    url(r'^(?P<article_id>[0-9]+)/$', views.article_read, name='article_read'),
    url(r'^(?P<article_id>[0-9]+)/theme_edit/$', views.article_edit_theme, name='article_edit_theme'),
    url(r'^article_add/$', views.article_add, name='article_add'),

    # summary edit/delete
    url(r'^(?P<article_id>[0-9]+)/summary_edit/$', views.summary_edit, name='summary_edit'),
    url(r'^(?P<article_id>[0-9]+)/summary_delete/$', views.summary_delete, name='summary_delete'),
    url(r'^(?P<article_id>[0-9]+)/rating_edit/$', views.rating_edit, name='rating_edit'),
    url(r'^(?P<article_id>[0-9]+)/article_delete/$', views.article_delete, name='article_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)