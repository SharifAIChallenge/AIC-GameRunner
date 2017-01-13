from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from storage.serializers import FileSerializer


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request):
        data = request.data
        data['owner_id'] = request.user.id
        serializer = FileSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'token': serializer.data['id']}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
