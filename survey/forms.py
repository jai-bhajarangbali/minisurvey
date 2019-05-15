from django.forms import ModelForm
from survey import models
from django import forms
from django.forms.formsets import formset_factory
from django.forms import  modelformset_factory


class SurveyCreationForm(ModelForm):
    class Meta:
        model = models.surveys
        fields = ['name']


class CreateSurvreyForm(forms.Form):
    name = forms.CharField(max_length = 250)
    private = forms.ChoiceField(choices = [(False,'public'),(True,'private')], widget = forms.RadioSelect())
    password = forms.CharField(max_length = 50, widget = forms.PasswordInput())




class AddQuestionForm(ModelForm):
    class Meta:
        model = models.questions
        fields = ['qtn','o1','o2','o3','o4']

AddQuestionFormSet = modelformset_factory(models.questions,
                                          form = AddQuestionForm,
                                          fields = ('qtn','o1','o2','o3','o4'),
                                          extra = 1)


class AnswerForm(forms.Form):
    ans = forms.ChoiceField(widget = forms.RadioSelect())
    '''
    def __init__(self, CHOICES, *args, **kwargs):
         super(forms.Form, self).__init__(*args, **kwargs)
         self.fields[ans].choices = CHOICES
    '''

    def set_choice(self,CHOICES):
        self.fields['ans'].choices = CHOICES


class PasswordForm(forms.Form):
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())




