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

    # Location of logfile in filesystem
    log_filepath = models.CharField(max_length=512, default='N/A')

    # Most recent lines from log file
    # There's a nicer way to do this... alas...
    recent_output_1 = models.CharField(max_length=512, default='-') # Most recent line in log
    recent_output_1_time = models.CharField(max_length=512, default='-')
    recent_output_2 = models.CharField(max_length=512, default='-')
    recent_output_2_time = models.CharField(max_length=512, default='-')
    recent_output_3 = models.CharField(max_length=512, default='-')
    recent_output_3_time = models.CharField(max_length=512, default='-')
    recent_output_4 = models.CharField(max_length=512, default='-')
    recent_output_4_time = models.CharField(max_length=512, default='-')
    recent_output_5 = models.CharField(max_length=512, default='-') # Fifth most recent line in log
    recent_output_5_time = models.CharField(max_length=512, default='-')

    cycles = models.CharField(max_length=16, default='N/A')

    # Metadata from log
    miseq_path = models.CharField(max_length=512, default='N/A')
    miseq_folder = models.CharField(max_length=512, default='N/A')
    fastq_destination = models.CharField(max_length=512, default='N/A')
    samplesheet = models.CharField(max_length=512, default='N/A')

    def __str__(self):
        return 'Run: {}'.format(self.run)
