from django.shortcuts import render
from django.views.generic import TemplateView

from django_tables2 import RequestConfig
from .tasks import miseq_directory_list
from subprocess import Popen, PIPE
import glob
import os

from .models import SipperRun

from .tables import SipperTable


# Create your views here.
class FileSystemViewer(TemplateView):
    template_name = 'sipper/miseq.html'

    def get(self, request, *args, **kwargs):

        out = miseq_directory_list('ls miseq/miseq_data')

        for miseq_run in out:
            run_object = SipperRun.objects.get_or_create(target_folder=miseq_run)
            print(run_object)

        miseq_runs = SipperRun.objects.all()

        table = SipperTable(miseq_runs)
        RequestConfig(request).configure(table)

        context = {
            'miseq_runs': miseq_runs,
            'table': table
        }

        return render(request,
                      self.template_name,
                      context)



