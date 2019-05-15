from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.http import HttpResponseForbidden
from .import models
from .forms import SurveyCreationForm
from .forms import *
from django.forms.formsets import formset_factory
from django.db import IntegrityError, transaction
from django.contrib import messages



def home(request):
    return render(request, 'survey/home.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user and user.is_active:
                login(request, user)
                return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'survey/signup.html', {'form': form})




@login_required(login_url = '/login/')
def profile(request):
    survey_list = models.surveys.objects.filter(user_id = request.user)
    context = {'username' : request.user.username , 'survey_list' : survey_list}
    return render(request, 'survey/profile.html', context)



@login_required(login_url = '/login/')
def log_out(request):
    logout(request)
    return redirect('home')



@login_required(login_url = '/login/')
def publish(request, pk):
    s = get_object_or_404(models.surveys, pk = pk)
    if s.user_id != request.user:
        return HttpResponseForbidden()

    s.published = True
    s.save()
    return redirect('profile')



@login_required(login_url = '/login/')
def create(request):
    if request.method == 'POST':
        form = CreateSurvreyForm(request.POST)
        if form.is_valid():
            s = models.surveys()
            s.name = form.cleaned_data.get('name')
            s.user_id = request.user
            s.private = form.cleaned_data.get('private')
            try:
                s.save()
                if s.private:
                    p = models.privatedetails(survey_id = s)
                    p.password = form.cleaned_data.get('password')
                    p.save()
                return redirect('detail',pk = s.id)
            except IntegrityError:
                messages.warning(request, 'survey with the following name already exists')

    else:
        form = CreateSurvreyForm()

    return render(request, 'survey/create.html', {'form':form})




@login_required(login_url = '/login/')
def detail(request, pk):
    s = get_object_or_404(models.surveys, pk=pk)
    if s.user_id != request.user:
        return HttpResponseForbidden()
    if s.published:
        return HttpResponseForbidden()

    qtns = models.questions.objects.filter(survey_id = s)
    return render(request, 'survey/detail.html', {'survey' : s , 'qtns' : qtns})




@login_required(login_url = '/login/')
def addqtn(request, pk):
    s = get_object_or_404(models.surveys, pk=pk)
    if s.user_id != request.user:
        return HttpResponseForbidden()
    if s.published:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit = False)
            q.survey_id = s
            q.save()
            return redirect('detail', pk = s.id)
    else:
        form = AddQuestionForm()

    return render(request, 'survey/addqtn.html', {'form':form})



@login_required(login_url = '/login/')
def deleteqtn(request, pk):
    qtn = get_object_or_404(models.questions, pk = pk)
    s = get_object_or_404(models.surveys, pk = qtn.survey_id_id)

    if s.user_id != request.user:
        return HttpResponseForbidden()

    qtn.delete()

    return redirect('detail', pk = s.id)



@login_required(login_url = '/login/')
def fill(request):
    excln = models.submissions.objects.filter(user_id = request.user)
    excln_list = [i.survey_id_id for i in excln]
    survey_list = models.surveys.objects.exclude(pk__in = excln_list).exclude(published = False).exclude(user_id = request.user)
    return render(request, 'survey/Srv_in.html', {'survey_list' : survey_list})


@login_required(login_url = '/login/')
def check(request, pk):
    s = get_object_or_404(models.surveys, pk = pk)

    if not s.private:
        return redirect('take', pk=pk, pwd=0)

    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            pwd = form.cleaned_data.get('password')
            if models.privatedetails.objects.get(survey_id = s).password == pwd:
                return redirect('take', pk = pk, pwd = pwd)
            messages.warning(request, 'Incorrect Password')
    else:
        form = PasswordForm()

    return render(request, 'survey/check.html', {'form':form})




@login_required(login_url = '/login/')
#@transaction.atomic
def take(request, pk, pwd):
    s = get_object_or_404(models.surveys, pk = pk)

    submitted = models.submissions.objects.filter(user_id = request.user)
    submitted = [i.survey_id for i in submitted]

    if s in submitted:
        return HttpResponseForbidden()
    if not s.published:
        return HttpResponseForbidden()
    if s.user_id == request.user:
        return HttpResponseForbidden()

    if s.private:
        if models.privatedetails.objects.get(survey_id=s).password != pwd:
            return redirect('check',pk=pk)

    qtns = models.questions.objects.filter(survey_id=s)
    AnswerFormSet = formset_factory(AnswerForm, extra=len(qtns))

    if request.method == 'POST':
        formset = AnswerFormSet(request.POST)
        i = 0
        for form in formset:
            CHOICES = [(1, qtns[i].o1),
                       (2, qtns[i].o2),
                       (3, qtns[i].o3),
                       (4, qtns[i].o4)]
            form.set_choice(CHOICES)

        if formset.is_valid():
            i = 0
            with transaction.atomic():
                for form in formset:
                    ans = form.cleaned_data.get('ans')
                    a = models.answers(user_id = request.user, ans = ans, qtn_id = qtns[i])
                    i += 1
                    try:
                        a.save()
                    except IntegrityError:
                        messages.warning(request, 'Please fill all questions')
                        success = False
                        break
                else:
                    success = True
                    models.submissions(user_id = request.user, survey_id = s).save()

            if success:
                return render(request, 'survey/success.html')

            transaction.rollback()
            return redirect('take', pk=pk, pwd=pwd)

    else:
        formset = AnswerFormSet()
        i = 0
        for form in formset:
            CHOICES = [(1, qtns[i].o1),
                       (2, qtns[i].o2),
                       (3, qtns[i].o3),
                       (4, qtns[i].o4)]
            form.set_choice(CHOICES)
            i += 1

    myzip = zip(formset,qtns)
    #return redirect('response', pk = s.id)
    return render(request, 'survey/take.html', {'formset':formset, 'myzip':myzip})




@login_required(login_url = '/login/')
def result(request, pk):
    s = get_object_or_404(models.surveys, pk = pk)
    if request.user != s.user_id:
        return HttpResponseForbidden()
    if not s.published:
        return HttpResponseForbidden()

    responses = models.submissions.objects.filter(survey_id = s)
    qtns = models.questions.objects.filter(survey_id = s)
    answers = models.answers.objects.filter(qtn_id__in = qtns).order_by('qtn_id_id')

    d1 = {}
    for a in answers:
        try:
            d1[a.qtn_id][a.ans-1] += 1
        except KeyError:
            d1[a.qtn_id] = [0,0,0,0]
            d1[a.qtn_id][a.ans-1] = 1

    d2 = {}
    for a in d1:
        d2[a] = list(map(lambda x: round(x*100/len(responses)), d1[a]))

    context = {'responses':len(responses), 'd1':d1, 'd2':d2}
    return render(request, 'survey/results.html',context)



