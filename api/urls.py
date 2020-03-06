from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    url('^schema/$', views.schema.SchemaView.as_view()),
    url(r'^storage/new_file/$', views.api_storage.FileUploadView.as_view(), name='create_file'),
    url(r'^storage/file/$', views.api_storage.FileDirectUploadView.as_view(), name='create_file'),
    url(r'^storage/new_file_from_url/$', views.api_storage.FileUploadFromUrlView.as_view(), name='create_file_from_url'),
    url(r'^storage/get_file/(?P<token>.+)/$', views.api_storage.FileDownloadView.as_view(), name='get_file'),
    url(r'^run/report/$', views.api_run.RunReportView.as_view(), name='run_report'),
    url(r'^run/run/$', views.api_run.RunCreateView.as_view(), name='create_run'),
]