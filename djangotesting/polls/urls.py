from django.conf.urls import url

from . import views

# this app_name is to help making the url dynamic
app_name = 'polls'

urlpatterns = [
    # ex: /polls/
    url(r'^$', views.IndexView.as_view(), name='index'),

    # ex: /polls/5/
    # ?P<pk> means to match the value with primary key ---
    # then [0-9]+ means match with a single integer
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),

    # ex: /polls/5/results/
    url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),

    # ex: /polls/5/vote/
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]
