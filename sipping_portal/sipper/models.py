from django.db import models
import datetime
import os


class SipperRun(models.Model):
    target_folder = models.CharField(max_length=256, primary_key=True)
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    genesippr_status = models.CharField(max_length=128,
                                        default="Unprocessed")

    def __str__(self):
        return 'Target Folder: {}'.format(self.target_folder)


class SippingMetadata(models.Model):
    run = models.OneToOneField(SipperRun, on_delete=models.CASCADE, primary_key=True)
    log_filepath = models.CharField(max_length=512, default='N/A')
    recent_output = models.CharField(max_length=512, default='N/A')
    time_elapsed = models.CharField(max_length=64, default='N/A')
    cycles = models.CharField(max_length=16, default='N/A')
    miseq_path = models.CharField(max_length=512, default='N/A')
    miseq_folder = models.CharField(max_length=512, default='N/A')
    fastq_destination = models.CharField(max_length=512, default='N/A')
    samplesheet = models.CharField(max_length=512, default='N/A')

    def __str__(self):
        return 'Run: {}'.format(self.run)
