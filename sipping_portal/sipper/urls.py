from django.conf.urls import url
from . import views


urlpatterns = [
    # Index
    url(r'^$', views.FileSystemViewer.as_view(), name='miseq'),

    # Active run table
    url(r'^active_run$', views.active_run, name='active_run'),
    url(r'^active_run_standalone$', views.active_run_standalone, name='active_run_standalone'),
]
