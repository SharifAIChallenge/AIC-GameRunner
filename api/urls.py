from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    url('^schema/$', views.schema.SchemaView.as_view()),
    url(r'^storage/new_file/$', views.api_storage.FileUploadView.as_view(), name='create_file'),
    url(r'^storage/get_file/(?P<token>[0-9a-z]+)/$', views.api_storage.FileDownloadView.as_view(), name='get_file'),
    url(r'^run/report/$', views.api_run.RunReportView.as_view(), name='run_report'),
    url(r'^run/run/$', views.api_run.RunCreateView.as_view(), name='create_run'),
]