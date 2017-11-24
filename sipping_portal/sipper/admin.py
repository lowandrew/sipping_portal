from django.contrib import admin

from .models import SipperRun, \
    SippingMetadata

# Register your models here.
admin.site.register(SipperRun)
admin.site.register(SippingMetadata)
