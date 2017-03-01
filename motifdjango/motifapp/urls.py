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

    # summary edit/delete
    url(r'^(?P<article_id>[0-9]+)/summary_edit/$', views.summary_edit, name='summary_edit'),
    url(r'^(?P<article_id>[0-9]+)/summary_delete/$', views.summary_delete, name='summary_delete'),
    url(r'^(?P<article_id>[0-9]+)/rating_creative_edit/$', views.rating_creative_edit, name='rating_creative_edit'),

]
