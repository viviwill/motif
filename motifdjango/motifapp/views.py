import sys

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Avg
from django.db.models import Q
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


import requests
from django.http import HttpResponse


# Homepage(index) list view
@method_decorator(login_required, name='dispatch')
class UserView(generic.ListView):
    # load the templates variable
    template_name = 'motifapp/user_view.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Article.objects.order_by('-add_date')[:10]

    def get_context_data(self, **kwargs):
        # create a context list here
        context = super(UserView, self).get_context_data(**kwargs)

        user = User.objects.get(username=self.kwargs['slug'])
        if user == self.request.user:
            context['is_login_user'] = True
            article_list = Article.objects.filter(storage__user=user.id).order_by(
                '-storage__add_date')
        else:
            # if it's not login user, filter out the private list
            context['is_login_user'] = False
            # !!!!!!!!!!!!!! be really fucking careful when you chaining filter
            article_list = Article.objects.filter(storage__public=True,
                                                  storage__user=user.id).order_by(
                '-storage__add_date')

        # check if following the user
        if not self.request.user.socialprofile.follows.filter(user=user.id):
            context['is_following'] = False
        else:
            context['is_following'] = True

        context['user'] = user
        # user saved article list
        context['user_saved_article'] = article_list.values('id', 'title', 'body_content',
                                                            'lead_image_url',
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

        # context['rating_stats'] = Storage.objects.annotate(
        #     number_of_rating=Count('rating_c'), number_of_summary=Count('summary')).values_list(
        #     'number_of_rating', 'number_of_summary')
        context['number_of_rating'] = Article.objects.filter(storage__user=user,
                                                             storage__rating_c__isnull=False).count()
        context['number_of_summary'] = Article.objects.filter(storage__user=user,
                                                              storage__summary__isnull=False).count()

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

        # get all public articles saved by follows
        public_saved = Article.objects.filter(
            storage__user__in=followings_list).filter(storage__public=True)

        # filter out duplicates
        distinct_saved = public_saved.distinct().order_by('-add_date')

        # prefetch to eliminate unfollow data
        following_saved_article = distinct_saved.prefetch_related(
            models.Prefetch('storage_set', queryset=Storage.objects.filter(
                user__in=followings_list).filter(public=True), to_attr='storage_from_followings'))

        context['following_saved_article'] = following_saved_article

        # rating
        distinct_saved_list = distinct_saved.values_list('id', flat=True).order_by('id')
        ratings = Article.objects.filter(id__in=distinct_saved_list).filter(
            storage__rating_c__isnull=False).annotate(
            total_rated=Count('storage__user'),
            avg_c=Avg('storage__rating_c'))
        context['ratings'] = ratings
        return context


def idea_of_motif(request):
    print "idea page here"

    return render(request, 'motifapp/idea_of_motif.html')


# individual article display view
@login_required
def article_read(request, article_id, **kwargs):
    # article_id = kwargs['article_id']

    # print "slug here", kwargs['slug']
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
    if request.method == "POST" and request.is_ajax():
        # update the score
        user = request.user
        user_storage = Storage.objects.filter(user_id=request.user).get(article_id=article_id)
        c_rating = request.POST['creative_star']
        if c_rating is not None:
            user_storage.rating_c = c_rating
            user_storage.save()

        art_temp = Article.objects.filter(id=article_id).filter(storage__rating_c__isnull=False)
        ratings = art_temp.annotate(total_rated=Count('storage__user'),
                                    avg_c=Avg('storage__rating_c'))
        try:
            storage_entry = Storage.objects.filter(user_id=user).get(article_id=article_id)
        except ObjectDoesNotExist:
            pass
        article = get_object_or_404(Article, pk=article_id)

        return render(request, 'motifapp/article_read_rating.html', locals())


# add article
def article_add(request):
    if request.method == "POST":
        print "Add article with url"
        web_url = request.POST['article_url']
        if request.POST['private'] == 'false':
            public = True
        else:
            public = False

        # call crawler
        article_crawl = motif_crawler.Uploadarticle(str(web_url))

        # 1) use sql to direct upload, with so much ascii shit going on
        # article_crawl.sql_upload()
        # target_id = article_crawl.get_article_id()

        # 2) use django api to create new instance
        article_value = article_crawl.sql_query_value
        # query_value = [title, author, web_url, lead_image_url, domain,
        #                body_content_string, pub_date, add_date, word_count]
        check_article = Article.objects.filter(web_url=article_value[2]).count()
        if check_article == 0:
            print "Article doesn't exist, add"
            new_article = Article(title=article_value[0], author=article_value[1],
                                  web_url=article_value[2], lead_image_url=article_value[3],
                                  domain=article_value[4], body_content=article_value[5],
                                  pub_date=article_value[6], add_date=article_value[7],
                                  word_count=article_value[8])
            new_article.save()
        else:
            print "Article existed"
        target_id = Article.objects.get(web_url=article_value[2]).id

        # check if the article existed, then update storage
        check_storage = Storage.objects.filter(article_id=target_id).filter(
            user=request.user).count()
        if check_storage == 0:
            print "Stroage doesn't exist, add article to storage"
            new_storage = Storage(article_id=target_id, user=request.user,
                                  add_date=timezone.now(), public=public)
            new_storage.save()
        else:
            print "Storage exist for user"
        return redirect('motifapp:index')


# edit article storage
def article_storage_edit(request, article_id):
    print "edit article storage setting for: ", article_id
    if request.method == "POST":
        user = request.user
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


def feedback_submit(request):
    if request.method == "POST":
        print "Feedback submit"
        feedback_url = request.POST['feedback_url']
        feedback_message = request.POST['feedback_message']
        user = request.user

        print "urlhere:", feedback_url

        Feedback(user=user, url=feedback_url, message=feedback_message).save()
        return JsonResponse({'message': 'Thank you!'})


# =============== User register/login/logout (NOT IN USE!!) ===================
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


def register_user(request):
    print "user registration"
    if request.user.is_authenticated():
        return redirect('motifapp:index')

    elif request.method == 'POST':
        invite_code = request.POST['invite_code']
        # if Invite.objects.filter(invite_code_given=False).filter(invite_code=invite_code).count()==0:
        if invite_code != 'lobster':
            return render(request, 'motifapp/registration_form.html',
                          {'error_message': 'Invalid invite code'})

        if User.objects.filter(username=request.POST['username']).count() != 0:
            return render(request, 'motifapp/registration_form.html',
                          {'error_message': 'Username taken'})

        if request.POST['username'].isdigit():
            return render(request, 'motifapp/registration_form.html',
                          {'error_message': 'Username cannot be just number'})

        form = UserForm(request.POST)
        if form.is_valid():
            print "form is valid"
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            print username, password, email

            user = form.save(commit=False)
            user.set_password(password)
            user.save()
            SocialProfile.objects.get_or_create(user=user)
            profile = SocialProfile.objects.get(user=user)
            profile.user_portrait = 'images/portrait/reading.jpg'
            profile.save()

            user = authenticate(username=username, password=password, email=email)
            everybody_is_friend(user)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('motifapp:index')

    return render(request, 'motifapp/registration_form.html')


def everybody_is_friend(target_user):
    print "let", target_user, "friends up with everybody "
    target_profile = target_user.socialprofile

    # for row in target_profile.follows.all():
    #     print "follows", row.user
    # for row in target_profile.followed_by.all():
    #     print "followed by", row.user

    # get everybody but admin and itself
    user_list = User.objects.exclude(username=target_user).exclude(username__icontains='admin')

    # everyone follows new kid and vice versa
    for row in user_list:
        other_profile = row.socialprofile
        target_profile.follows.add(other_profile)
        other_profile.follows.add(target_profile)


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


# testing view
def testing_view(request):
    variable = request.path
    return render(request, 'motifapp/zzz_testing.html', {'variable': variable})
