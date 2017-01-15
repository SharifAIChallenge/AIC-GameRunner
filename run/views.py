from rest_framework.parsers import JSONParser
from .serializers import RunCreateSerializer, RunReportSerializer
from .models import Run
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class RunCreateView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        runs_json = JSONParser().parse(request)
        # validate if the data is a list
        if runs_json is not list:
            return Response({'result': None}, status=status.HTTP_400_BAD_REQUEST)
        result = []
        for run_json in runs_json:
            serializer = RunCreateSerializer(data=run_json)
            if serializer.is_valid():
                run = serializer.save()
                result.append(run.id)  # We will replace id by token
            else:
                result.append(serializer.error_messages)
        return Response({'result': result}, status=status.HTTP_207_MULTI_STATUS)


class RunReportView(APIView):
    def get(self, request):
        data = JSONParser().parse(request)
        runs = Run.objects.all().query(end_time_gte=data['from_time'])
        result = []
        for run in runs:
            serializer = RunReportSerializer(run)
            result.append(serializer.data)
        return Response(result)
