from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import generic
from django.views.generic import View
from django.db.models import Count

# ------------
from .forms import UserForm
from .models import Article, Storage

# ------------
import sys

sys.path.append('/Users/viviwill/Desktop/motif/')
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
        article_list = Article.objects.filter(storage__user=user.id).order_by('-add_date')
        context['user_saved_article'] = article_list.values('id', 'title', 'storage__add_date')

        # context['saved_list'] = Article.objects.annotate(number_of_entries=Count('storage')).order_by('-number_of_entries')
        return context


# individual article detailed view
def article_read(request, article_id):
    user = request.user
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'motifapp/article_read.html', {'article': article, 'user': user})


# add summary
def summary_add(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.method == "POST":
        print "Post is here:", request.POST['summary']
        # you need to render the same thing as def article_read, to show the info on same page
        return redirect('motifapp:article_read', article_id)


# add article
def article_add(request):
    print "is adding an article"
    if request.method == "POST":
        web_url = request.POST['web_url']
        article_crawl = motif_crawler.Uploadarticle(str(web_url))
        article_crawl.sql_upload()

        # update storage
        target_id = article_crawl.get_article_id()
        s = Storage(article_id=target_id, user=request.user, add_date=timezone.now())
        s.save()
        return redirect('motifapp:index')


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
    return render(request, 'motifapp/login.html', context)
