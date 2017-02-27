from django.conf.urls import url
from . import views

app_name = 'motifapp'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    # register, login, logout
    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),

    # individual article page
    url(r'^(?P<article_id>[0-9]+)/$', views.article_read, name='article_read'),
    url(r'^article_add/$', views.article_add, name='article_add'),
    url(r'^(?P<article_id>[0-9]+)/summary_add/$', views.summary_add, name='summary_add'),
]
