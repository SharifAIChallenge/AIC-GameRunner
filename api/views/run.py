from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import RunCreateSerializer, RunReportSerializer
from run.models import Run


class RunCreateView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        runs_json = JSONParser().parse(request)
        # validate if the data is a list
        if not isinstance(runs_json, list):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        result = []
        for run_json in runs_json:
            serializer = RunCreateSerializer(data=run_json)
            if serializer.is_valid():
                run = serializer.save()
                result.append({
                    'success': True,
                    'run_id': run.id
                })
            else:
                result.append({
                    'success': False,
                    'errors': serializer.error_messages
                })
        return Response(result, status=status.HTTP_200_OK)


class RunReportView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        runs = Run.objects.all().filter(end_time__gte=data['from_time'])
        result = []
        for run in runs:
            serializer = RunReportSerializer(run)
            result.append(serializer.data)
        return Response(result)
