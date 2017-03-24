import sys

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic import View
from django.views.generic.edit import FormMixin

from .forms import *
from .models import *

import os

# sys.path.append('/Users/viviwill/Desktop/motif/')
from crawler import motif_crawler


# Homepage(index) list view
@method_decorator(login_required, name='dispatch')
class IndexView(generic.ListView):
    # load the templates variable
    template_name = 'motifapp/index.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Article.objects.order_by('-add_date')[:10]

    def get_context_data(self, **kwargs):
        # create a context list here
        context = super(IndexView, self).get_context_data(**kwargs)

        # list of different context starts here, then return to use in views
        user = self.request.user
        context['user'] = self.request.user

        # user saved article list
        article_list = Article.objects.filter(storage__user=user.id).order_by('-storage__add_date')
        context['user_saved_article'] = article_list.values('id', 'title', 'lead_image_url',
                                                            'domain', 'word_count',
                                                            'storage__add_date',
                                                            'storage__summary',
                                                            'storage__summary_modified_date',
                                                            'storage__rating_i',
                                                            'storage__rating_c',
                                                            'storage__public')
        ratings = Article.objects.filter(storage__rating_c__isnull=False).annotate(
            total_rated=Count('storage__user'),
            avg_c=Avg('storage__rating_c'))
        context['ratings'] = ratings
        return context


def article_delete(request, article_id):
    user_storage = Storage.objects.filter(user_id=request.user).get(article_id=article_id)
    user_storage.delete()
    return redirect('motifapp:index')


# change privacy setting for saved article
def article_public_edit(request, article_id):
    user_storage = Storage.objects.filter(user_id=request.user).get(article_id=article_id)
    user_storage.public = not user_storage.public
    user_storage.save()
    return JsonResponse({'public': user_storage.public})


@method_decorator(login_required, name='dispatch')
class DiscoverView(generic.ListView):
    model = Article
    template_name = 'motifapp/discover.html'
    page_template = 'motifapp/discover_entry.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        return Article.objects.order_by('-add_date')[:20]

    def get_context_data(self, **kwargs):
        context = super(DiscoverView, self).get_context_data(**kwargs)
        user = self.request.user

        # get all followings
        followings = user.socialprofile.follows.all()
        followings_list = list(followings.values_list('user', flat=True).order_by('user'))

        # get all article following saved with distinct, prefetch to eliminate unfollow data
        distinct_saved = Article.objects.filter(
            storage__user__in=followings_list).distinct().order_by('-add_date')
        following_saved_article = distinct_saved.prefetch_related(
            models.Prefetch('storage_set', queryset=Storage.objects.filter(
                user__in=followings_list), to_attr='storage_from_followings'))
        context['following_saved_article'] = following_saved_article

        # rating
        distinct_saved_list = distinct_saved.values_list('id', flat=True).order_by('id')
        ratings = Article.objects.filter(id__in=distinct_saved_list).filter(storage__rating_c__isnull=False).annotate(
            total_rated=Count('storage__user'),
            avg_c=Avg('storage__rating_c'))
        context['ratings'] = ratings
        return context


# individual article display view
@login_required
def article_read(request, article_id):
    user = request.user
    storage_entry = None

    # rating for this article
    art_temp = Article.objects.filter(id=article_id).filter(storage__rating_c__isnull=False)
    ratings = art_temp.annotate(total_rated=Count('storage__user'), avg_c=Avg('storage__rating_c'))

    # gather all storage data from article
    try:
        storage_entry = Storage.objects.filter(user_id=user).get(article_id=article_id)
    except ObjectDoesNotExist:
        pass

    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'motifapp/article_read.html',
                  {'article': article,
                   'user': user,
                   'storage_entry': storage_entry,
                   'reading_time': article.word_count / 200,
                   'ratings': ratings
                   })


# add summary
def summary_edit(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    # if it's POST and summary not empty, then perform POST
    # otherwise go to edit page
    if request.method == "POST" and request.POST['summary'].strip():
        summary = request.POST['summary']
        # you need to render the same thing as def article_read, to show the info on same page
        user_storage = Storage.objects.filter(user_id=request.user).get(article_id=article_id)
        # upload the summary and mod_date, then save
        user_storage.summary = summary
        user_storage.summary_modified_date = timezone.now()
        user_storage.save()

        return JsonResponse({'update_summary': summary})
    else:
        user = request.user
        summary = Storage.objects.filter(user_id=user).get(article_id=article_id).summary
        article = get_object_or_404(Article, pk=article_id)
        return render(request, 'motifapp/summary_edit.html',
                      {'article': article, 'user': user, 'summary': summary})


# delete summary
def summary_delete(request, article_id):
    user_storage = Storage.objects.filter(user_id=request.user).get(article_id=article_id)
    # upload the summary and mod_date, then save
    user_storage.summary = None
    user_storage.summary_modified_date = None
    user_storage.save()

    # redirect to individual article page
    return redirect('motifapp:article_read', article_id)


# edit rating
def rating_edit(request, article_id):
    if request.method == "POST":
        user_storage = Storage.objects.filter(user_id=request.user).get(article_id=article_id)
        c_rating = request.POST.get('creative-star')
        i_rating = request.POST.get('informative-star')
        print "POST creative rating: ", c_rating
        print "POST informative rating: ", i_rating

        # update the score
        if c_rating is not None:
            user_storage.rating_c = c_rating
        if i_rating is not None:
            user_storage.rating_i = i_rating
        user_storage.save()
        return redirect('motifapp:article_read', article_id)


# add article
def article_add(request):
    if request.method == "POST":
        print "Add article with url"
        web_url = request.POST['web_url']
        article_crawl = motif_crawler.Uploadarticle(str(web_url))
        article_crawl.sql_upload()

        # update storage
        target_id = article_crawl.get_article_id()
        check = Storage.objects.filter(article_id=target_id).filter(user=request.user).count()
        if check == 0:
            s = Storage(article_id=target_id, user=request.user, add_date=timezone.now())
            s.save()
        else:
            print "Article exsited in user storage"
        return redirect('motifapp:index')


# edit article storage
def article_storage_edit(request, article_id):
    print "edit article storage setting for: ", article_id
    if request.method == "POST":
        user=request.user
        try:
            storage_entry = Storage.objects.filter(user_id=user).get(article_id=article_id)
            storage_entry.delete()
            storage_status = "SAVE"
        except ObjectDoesNotExist:
            new_storage = Storage(article_id=article_id, user=user, add_date=timezone.now())
            new_storage.save()
            storage_status = "SAVED"
        return JsonResponse({'storage_status': storage_status})


def article_edit_theme(request, article_id):
    print "changing font size"
    if request.method == "POST":
        profile = request.user.socialprofile
        change = request.POST['font_size']
        if change == "plus":
            if profile.theme_font_size < 2:
                profile.theme_font_size += 0.2
        elif change == 'minus':
            if profile.theme_font_size > 1:
                profile.theme_font_size -= 0.2
        profile.save()

        return JsonResponse({'font_size': str(profile.theme_font_size) + 'rem'})


# =============== User register/login/logout ===================
class UserFormView(View):
    form_class = UserForm
    templates_name = 'motifapp/registration_form.html'

    # display a blank form for new user
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.templates_name, {'form': form})

    # process form data and register
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            # cleaned (normalized) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # django built in way to set password
            user.set_password(password)
            user.save()

            # create a profile after user successfully register
            SocialProfile.objects.get_or_create(user=user)

            # take user and pw, check db if they exist/active
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('motifapp:index')

        # if user didn't login, here is the form to try again
        return render(request, self.templates_name, {'form': form})


# Login View
def login_user(request):
    # if user is logged in, then redirect to homepage
    if request.user.is_authenticated():
        return redirect('motifapp:index')

    # otherwise do following
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('motifapp:index')
            else:
                return render(request, 'motifapp/login.html',
                              {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'motifapp/login.html',
                          {'error_message': 'Invalid login'})
    return render(request, 'motifapp/login.html')


# logout view
def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        'form': form,
    }
    return redirect('motifapp:login')


class UserProfile(generic.DetailView, FormMixin):
    model = User
    slug_field = "username"
    template_name = "motifapp/user_profile.html"
    form_class = ProfileForm

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        context['form'] = ProfileForm(initial={'username': self.request.user})
        return context

    def post(self, request, *args, **kwargs):
        # get the posted form, then validate
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            # cleaned (normalized) data
            username = form.cleaned_data['username']
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            portrait = form.cleaned_data['user_portrait']
            portrait.name = str(self.request.user.id) + '.png'

            # if the file exist, delete
            try:
                path = 'images/portrait'
                os.remove(os.path.join(settings.MEDIA_ROOT, path, portrait.name))
            except OSError:
                pass

            update_profile = SocialProfile.objects.get(user=self.request.user)
            update_profile.user_portrait = portrait
            update_profile.save()

        return render(request, self.template_name, {'form': form})
