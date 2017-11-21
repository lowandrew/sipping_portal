from django.db import models
import datetime
import os


# Create your models here.
class SipperRun(models.Model):
    target_folder = models.CharField(max_length=256, primary_key=True)
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    genesippr_status = models.CharField(max_length=128,
                                        default="Unprocessed")

