from django.conf.urls import url

from . import views

app_name = 'api'
urlpatterns = [
    url(r'^storage/new_file$', views.storage.FileUploadView.as_view(), name='create_file'),
    url(r'^storage/get_file$', views.storage.FileDownloadView.as_view(), name='get_file'),
]
