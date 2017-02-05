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
            return Response({'result': 'Provided data is not a list.'}, status=status.HTTP_400_BAD_REQUEST)
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
    def post(self, request):
        data = JSONParser().parse(request)
        # todo put the last time report view is called as default for 'time' param.
        if 'time' in data:
            from_time = data['time']
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        runs = Run.objects.all().filter(end_time__gte=from_time)
        result = []
        for run in runs:
            serializer = RunReportSerializer(run)
            result.append(serializer.data)
        return Response(result)
