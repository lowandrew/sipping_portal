from django.forms import ModelForm, HiddenInput
from .models import SipperRun
from django.shortcuts import HttpResponse


class RunForm(ModelForm):

    class Meta:
        model = SipperRun
        widgets = {'target_folder': HiddenInput()}
        fields = ['target_folder']

    @staticmethod
    def submit():
        return HttpResponse('status=201')
