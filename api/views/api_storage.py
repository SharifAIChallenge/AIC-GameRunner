import os

import coreapi
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser

from api.views.utils import define_coreapi_field
from storage.serializers import FileSerializer
from storage.models import File


class DefaultNamedFileUploadParser(FileUploadParser):
    def get_filename(self, *args, **kwargs):
        name = super(DefaultNamedFileUploadParser, self).get_filename(*args, **kwargs)
        if not name:
            return "uploaded_file"
        else:
            return name


class FileUploadView(APIView):
    parser_classes = (DefaultNamedFileUploadParser, )

    @define_coreapi_field(name="file", location="body", required=True, )
    def put(self, request):
        serializer = FileSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.auth)
            return Response({'token': serializer.data['id']},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDownloadView(APIView):

    def get(self, request, token):
        try:
            file = File.objects.get(id=token, owner=request.auth)
            file_name = token
            response = HttpResponse(file.file, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
            return response
        except File.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
