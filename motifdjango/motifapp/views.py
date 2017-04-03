import sys

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
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
import re

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
                user__in=followings_list).filter(public=True).order_by('-upvotes'),
                            to_attr='storage_from_followings'))

        context['following_saved_article'] = following_saved_article

        # rating
        distinct_saved_list = distinct_saved.values_list('id', flat=True).order_by('id')
        ratings = Article.objects.filter(id__in=distinct_saved_list).filter(
            storage__rating_c__isnull=False).annotate(
            total_rated=Count('storage__user'),
            avg_c=Avg('storage__rating_c'))
        context['ratings'] = ratings

        # detect user interaction with summary
        context['user_activity'] = Activity.objects.filter(user=user,
                                                           vote_value=1).values_list(
            'storage_interact', flat=True)
        # for row in context['user_activity']:
        #     print row
        return context


def activity(request):
    user = request.user
    activities = Activity.objects.filter(user=user)
    return render(request, 'motifapp/activity.html', {'activities': activities})


def reset_summary_vote():
    for storage in Storage.objects.all():
        storage.upvotes = 0
        storage.save()


def upvote_summary(request):
    if request.method == "POST":
        storage_id = request.POST['storage_id']
        print "Upvote Summary for storage:", storage_id
        summary_storage = Storage.objects.get(id=storage_id)

        try:
            # if existed, update time, vote
            act = Activity.objects.get(user=request.user, storage_interact=summary_storage,
                                       type='UP')
            act.activity_date = timezone.now()

            if act.vote_value != 0:
                summary_storage.upvotes -= 1
                act.vote_value = 0
            else:
                summary_storage.upvotes += 1
                act.vote_value = 1
            summary_storage.save()
            act.save()
        except ObjectDoesNotExist:
            act = Activity.objects.create(user=request.user, storage_interact=summary_storage,
                                          type='UP',
                                          activity_date=timezone.now())
            summary_storage.upvotes += 1
            summary_storage.save()
            act.vote_value = 1
            act.save()
            print "add 1 note"

        return JsonResponse({'voted': act.vote_value})


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
                    return redirect('motifapp:idea_of_motif')

    return render(request, 'motifapp/registration_form.html')


def everybody_is_friend(target_user):
    print "let", target_user, "friends up with everybody "
    target_profile = target_user.socialprofile

    # for row in target_profile.follows.all():
    #     print "follows", row.user
    # for row in target_profile.followed_by.all():
    #     print "followed by", row.user

    # if it's testing account, only follows viviwill. Else get everybody but admin and itself
    if 'testing' in target_user.username:
        user_list = User.objects.filter(username='viviwill')
    else:
        user_list = User.objects.exclude(username=target_user).exclude(
            username__icontains='admin').exclude(username__icontains='test')

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

        current_path = self.request.path
        if 'activity' in current_path:
            context['current'] = 'activity'
        elif 'profile' in current_path:
            context['current'] = 'profile'
        elif 'follower' in current_path:
            context['current'] = 'follower'
        elif 'following' in current_path:
            context['current'] = 'following'

        user = User.objects.get(username=self.kwargs['slug'])
        if user == self.request.user:
            context['is_login_user'] = True
        else:
            context['is_login_user'] = False

        context['form'] = ProfileForm(initial={'username': self.request.user})
        if not self.request.user.socialprofile.follows.filter(user=user.id):
            context['is_following'] = False
        else:
            context['is_following'] = True
        print context['is_following']

        context['number_of_rating'] = Article.objects.filter(storage__user=user,
                                                             storage__rating_c__isnull=False).count()
        context['number_of_summary'] = Article.objects.filter(storage__user=user,
                                                              storage__summary__isnull=False).count()

        # activity
        # context['activities'] = Activity.objects.filter(user=user)
        context['activities'] = Activity.objects.filter(
            Q(user=user) | Q(storage_interact__user=user), ~Q(vote_value='0')).order_by(
            '-activity_date')

        return context

    def post(self, request, *args, **kwargs):
        print "this is a post"
        form = ProfileForm(self.request.POST, self.request.FILES)
        slug = kwargs['slug']

        if form.is_valid():
            print "Update user, form is valid"

            # user = form.save(commit=False)
            # cleaned (normalized) data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            portrait = form.cleaned_data['user_portrait']
            # print "oldfilename is: ", portrait.name
            # portrait.name = re.sub(r'.*\.', '.', portrait.name)
            # print "new filename is: ", portrait.name

            # portrait.name = str(self.request.user.id) + '.png'
            # print "username", username, "email", email, "old_password", old_password, "portrait", portrait

            if portrait:
                print "there is something"
            else:
                print "no pic"

            # update portrait if necessary
            if portrait:
                print "update portrait"
                update_profile = SocialProfile.objects.get(user=request.user)
                portrait.name = request.user.socialprofile.user_portrait.name
                print "name is:", portrait.name

                try:
                    path = 'images/portrait'
                    os.remove(os.path.join(settings.MEDIA_ROOT, path, portrait.name))
                except OSError:
                    pass
                update_profile.user_portrait = portrait
                update_profile.save()


            # portrait.name = str(self.request.user.id) + '.png'
            # # if the file exist, delete
            # try:
            #     path = 'images/portrait'
            #     os.remove(os.path.join(settings.MEDIA_ROOT, path, portrait.name))
            # except OSError:
            #     pass
            #
            # update_profile = SocialProfile.objects.get(user=self.request.user)
            # update_profile.user_portrait = portrait
            # update_profile.save()



            # update user info if necessary
            if username != '' or new_password != '' or email != '':
                print "update user info"
                user_obj = authenticate(username=request.user, password=old_password)
                if user_obj is not None:
                    print "Password correct"

                    if username != '':
                        user_obj.username = username
                        slug = username
                    if new_password != '':
                        user_obj.set_password(new_password)
                    if email != '':
                        user_obj.email = email
                    user_obj.save()
                    update_session_auth_hash(request, user_obj)
                else:
                    print "Password wrong"

            return redirect('motifapp:user_profile', slug=slug)
        return JsonResponse({'font_size': 'haha'})


# idea view
def idea_of_motif(request):
    print "idea page here"

    return render(request, 'motifapp/idea_of_motif.html')


# testing view
def testing_view(request):
    variable = request.path
    return render(request, 'motifapp/zzz_testing.html', {'variable': variable})
