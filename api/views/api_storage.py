import requests
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser

from api.permissions import IsAuthenticated
from api.views.utils import define_coreapi_field
from storage.serializers import FileSerializer, FileUrlSerializer, FileDirectSerializer
from storage.models import File


class DefaultNamedFileUploadParser(FileUploadParser):
    def get_filename(self, *args, **kwargs):
        name = super(DefaultNamedFileUploadParser, self).get_filename(*args, **kwargs)
        if not name:
            return "uploaded_file"
        else:
            return name


class FileUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (DefaultNamedFileUploadParser, )

    @define_coreapi_field(name="file", location="body", required=True, )
    def put(self, request):
        serializer = FileSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.auth)
            return Response({'token': serializer.data['id']},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDirectUploadView(APIView):
    parser_classes = (parsers.MultiPartParser, )

    @define_coreapi_field(name="file", location="body", required=True, )
    def post(self, request):
        serializer = FileDirectSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            f = File.objects.create(owner_id=settings.SITE_TOKEN, file=serializer.validated_data['file'])
            try:
                response = f.send_token(serializer.validated_data['user_token'],
                                        serializer.validated_data['language'],
                                        request.get_host(),
                                        request.META.get('HTTP_ACCEPT_LANGUAGE'))
            except requests.RequestException:
                return Response("Something Went Wrong", status=status.HTTP_400_BAD_REQUEST)
            return Response(response.json(), status=response.status_code)

        return Response("Bad Request", status=status.HTTP_400_BAD_REQUEST)


class FileUploadFromUrlView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = FileUrlSerializer(data=request.data)

        if serializer.is_valid():
            file = File(owner=request.auth)
            try:
                file.retrieve_from_url(serializer.validated_data['url'])
            except File.FileNotFoundError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)

            file.save()
            return Response({'token': file.id},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDownloadView(APIView):
    permission_classes = (IsAuthenticated,)

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
