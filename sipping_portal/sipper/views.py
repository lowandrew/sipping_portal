from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, FormView
from django_tables2 import RequestConfig
from django.core import serializers
from .tasks import miseq_directory_list, start_sipping
from subprocess import Popen, PIPE
import glob
import os
import logging

from .forms import RunForm
from .models import SipperRun, SippingMetadata

from .tables import SipperTable


# Create your views here.
class FileSystemViewer(TemplateView):
    template_name = 'sipper/miseq.html'
    form_class = RunForm

    def get(self, request, *args, **kwargs):
        out = miseq_directory_list('ls miseq/')

        # Debug
        for miseq_run in out:
            run_object = SipperRun.objects.get_or_create(target_folder=miseq_run)
            print('Run Object: {}'.format(run_object))

        miseq_runs = SipperRun.objects.all()

        table = SipperTable(miseq_runs)
        RequestConfig(request).configure(table)

        context = {
            'miseq_runs': miseq_runs,
            'table': table,
        }

        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        target_folder = request.POST.get('miseq_run')
        print('Target folder: {}\n'.format(target_folder))

        run_model = SipperRun.objects.get(target_folder=target_folder)

        SippingMetadata.objects.create(run=run_model)
        print('Created SippingMetadata object...\n')

        run_model.genesippr_status = 'Processing'
        run_model.save()
        print('Attempted to set genesippr_status to Processing\n'
                      'Actual value is: {}'.format(run_model.genesippr_status))

        json_model = serializers.serialize('json', [run_model])
        start_sipping(target_folder, json_model)

        return HttpResponseRedirect('#')






