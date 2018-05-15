import django_tables2 as tables
from .models import SipperRun


class SipperTable(tables.Table):
    class Meta:
        model = SipperRun
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table'}
        exclude = ('updated_date', )

#table-sm table-hover table-responsive table-bordered
