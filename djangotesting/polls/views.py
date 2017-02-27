from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Question, Choice


# Use 2 generic views: ListView and DetailView
# 1) Display a list of objects
# 2) display a detail page for a particular object
class IndexView(generic.ListView):
    # load the templates variable
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    # queryset = generic.Individual.objects.all()

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:10]

    # use get_context_data to create a context[] to show in html
    def get_context_data(self, **kwargs):
        # create a context list here
        context = super(IndexView, self).get_context_data(**kwargs)

        # list of different context starts here, then return for use
        context['latest'] = Question.objects.order_by('-pub_date')[:10]
        context['earliest_question_list'] = Question.objects.order_by('pub_date')[:10]

        # can display items from different models as well
        context['all_choice'] = Choice.objects.order_by('choice_text')
        return context


# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     # this returns the target question object
#     return render(request, 'polls/detail.html', {'question': question})

class DetailView(generic.DetailView):
    # model attribute tells the view what model it is associated with
    # primary key = pk
    model = Question

    # templates name tells django to look for specific html templates
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    # see tutorial part 4 for POST
    question = get_object_or_404(Question, pk=question_id)
    try:
        # this line get the posted target
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # if we get to this part of code, means everything is working
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
