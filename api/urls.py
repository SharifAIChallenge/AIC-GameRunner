from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    url(r'^storage/new_file$', views.api_storage.FileUploadView.as_view(), name='create_file'),
    url(r'^storage/get_file$', views.api_storage.FileDownloadView.as_view(), name='get_file'),
    url(r'^run/report$', views.run.RunReportView.as_view(), name='run_report'),
    url(r'^run/run$', views.run.RunCreateView.as_view(), name='create_run'),
]