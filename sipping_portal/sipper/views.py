from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, FormView, DetailView
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

        # Get all run objects
        miseq_runs = SipperRun.objects.all()

        # Table setup
        table = SipperTable(miseq_runs)
        RequestConfig(request).configure(table)

        # Context
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

        # Grab MiSeq run selected by user
        run_model = SipperRun.objects.get(target_folder=target_folder)

        # Create object in DB for metadata storage
        SippingMetadata.objects.create(run=run_model)
        print('Created SippingMetadata object...\n')

        # Get created object
        run_metadata_model = SippingMetadata.objects.get(run=run_model)

        # Update Genesippr status
        run_model.genesippr_status = 'Processing'
        run_model.save()
        print('Attempted to set genesippr_status to Processing\n'
                      'Actual value is: {}'.format(run_model.genesippr_status))

        # Set log file location
        run_metadata_model.log_filepath = 'sipping_portal/media/{target_folder}/portal.log'.format(target_folder=target_folder)
        run_metadata_model.save()

        # Serialize model instance so it can be passed to sipping function
        json_model = serializers.serialize('json', [run_model])
        json_metadata_model = serializers.serialize('json', [run_metadata_model])
        start_sipping(target_folder, json_model, json_metadata_model)

        # Update page
        return HttpResponseRedirect('#')

def active_run(request):
    # Get current run (if any)
    currently_processing_run = SipperRun.objects.filter(genesippr_status='Processing')
    if len(currently_processing_run) > 1:
        print('Something is wrong. Detected >1 "Processing" GenesipprV2 run.')

    try:
        currently_processing_run = SipperRun.objects.filter(genesippr_status='Processing')[0]
    except IndexError:
        currently_processing_run = None

    current_run_metadata = SippingMetadata.objects.get(run=currently_processing_run.pk)

    context = {
        'currently_processing_run' : currently_processing_run,
        'current_run_metadata' : current_run_metadata,
    }

    return render(request,
                  'sipper/active_run.html',
                  context)
