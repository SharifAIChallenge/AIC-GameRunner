import os
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from storage.serializers import FileSerializer
from storage.models import File


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request):
        serializer_data = dict()
        serializer_data['owner'] = request.auth
        serializer_data['file'] = request.data['file']
        serializer = FileSerializer(data=serializer_data)

        if serializer.is_valid():
            serializer.save()
            return Response({'token': serializer.data['id']}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDownloadView(APIView):
    def post(self, request):
        if 'token' in request.data:
            try:
                file = File.objects.get(id=request.data['token'], owner=request.auth)
                file_name = os.path.basename(file.file.name)
                response = HttpResponse(file.file, content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
                return response
            except File.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
