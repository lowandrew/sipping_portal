from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, FormView, DetailView
from django_tables2 import RequestConfig
from django.core import serializers
from .tasks import miseq_directory_list, start_sipping
from .forms import RunForm
from .models import SipperRun, SippingMetadata
from .tables import SipperTable
import os


# Create your views here.
class FileSystemViewer(TemplateView):
    template_name = 'sipper/miseq.html'
    form_class = RunForm

    def get(self, request, *args, **kwargs):

        # Check for new runs, and create objects for them as necessary.
        folders = miseq_directory_list('ls miseq')
        for folder in folders:
            if not SipperRun.objects.filter(target_folder=folder.decode('utf-8')).exists():
                SipperRun.objects.create(target_folder=folder.decode('utf-8'))

        # Get all run objects.
        miseq_runs = SipperRun.objects.all()

        # Count number of currently processing runs. Should be 0 or 1.
        # This value is used to determine whether or not to display buttons to activate a run.
        num_processing_runs = len(SipperRun.objects.filter(genesippr_status='Processing'))

        # Table setup
        table = SipperTable(miseq_runs)
        RequestConfig(request).configure(table)

        # Context
        context = {
            'miseq_runs': miseq_runs,
            'table': table,
            'num_processing_runs': num_processing_runs
        }

        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        print('Post request detected')

        target_folder = request.POST.get('miseq_run_target')

        print('Target folder: {}\n'.format(target_folder))

        # Grab MiSeq run selected by user
        run_model = SipperRun.objects.get(target_folder=target_folder)

        # Make sure the form doesn't get submitted more than once - this is a problem
        if run_model.genesippr_status == 'Complete' or run_model.genesippr_status == 'Processing':
            print('Avoiding disaster!')
            return None

        # Create object in DB for metadata storage
        SippingMetadata.objects.create(run=run_model)
        print('Created SippingMetadata object...\n')

        # Get created object
        run_metadata_model = SippingMetadata.objects.get(run=run_model)

        # Update Genesippr status
        run_model.genesippr_status = 'Processing'
        run_model.save()

        # Set log file location
        run_metadata_model.log_filepath = 'sipping_portal/media/{target_folder}/portal.log'.format(target_folder=target_folder)
        run_metadata_model.save()

        # Serialize model instance so it can be passed to sipping function
        json_model = serializers.serialize('json', [run_model])
        json_metadata_model = serializers.serialize('json', [run_metadata_model])

        # Start Genesippr
        start_sipping(target_folder, json_model, json_metadata_model)

        # Redirect
        return HttpResponseRedirect('active_run_standalone')


def active_run(request):
    # Get current run (if any)
    currently_processing_run = SipperRun.objects.filter(genesippr_status='Processing')
    if len(currently_processing_run) > 1:
        print('Something is wrong. Detected >1 "Processing" GenesipprV2 run.')

    try:
        currently_processing_run = SipperRun.objects.filter(genesippr_status='Processing')[0]
    except IndexError:
        currently_processing_run = None

    try:
        current_run_metadata = SippingMetadata.objects.get(run=currently_processing_run.pk)
    except AttributeError:
        current_run_metadata = None

    context = {
        'currently_processing_run': currently_processing_run,
        'current_run_metadata': current_run_metadata,
        'currently_processing_run' : currently_processing_run,
        'current_run_metadata' : current_run_metadata,
    }

    return render(request,
                  'sipper/active_run.html',
                  context)


def active_run_standalone(request):
    # Get all run objects
    miseq_runs = SipperRun.objects.all()

    # Get current run (if any)
    currently_processing_run = SipperRun.objects.filter(genesippr_status='Processing')
    if len(currently_processing_run) > 1:
        print('Something is wrong. Detected >1 "Processing" GenesipprV2 run.')

    try:
        currently_processing_run = SipperRun.objects.filter(genesippr_status='Processing')[0]
    except IndexError:
        currently_processing_run = None

    try:
        current_run_metadata = SippingMetadata.objects.get(run=currently_processing_run.pk)
    except AttributeError:
        current_run_metadata = None

    context = {
        'miseq_runs': miseq_runs,
        'currently_processing_run' : currently_processing_run,
        'current_run_metadata' : current_run_metadata,
    }

    return render(request,
                  'sipper/active_run_standalone.html',
                  context)
