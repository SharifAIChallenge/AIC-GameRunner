from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer
from rest_framework.views import APIView

from api.serializers import RunCreateSerializer, RunReportSerializer
from api.views.utils import define_coreapi_field
from run.models import Run
import datetime
from django.utils import timezone


class RunCreateView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        # TODO: Use a ListSerializer
        runs_json = JSONParser().parse(request)
        # validate if the data is a list
        if not isinstance(runs_json, list):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        result = []
        for run_json in runs_json:
            serializer = RunCreateSerializer(data=run_json)
            if serializer.is_valid():
                run = serializer.save(owner=request.auth)
                result.append({
                    'success': True,
                    'run_id': run.id
                })
            else:
                result.append({
                    'success': False,
                    'errors': serializer.errors
                })
        return Response(result, status=status.HTTP_200_OK)

    def get_serializer(self):
        return RunCreateSerializer(many=True)


class RunReportView(APIView):
    @define_coreapi_field(name="time", location="query", required=True, type="float", )
    def get(self, request):
        data = request.GET
        # todo put the last time report view is called as default for 'time' param.
        # TODO Use filters
        if 'time' in data:
            try:
                from_time = timezone.make_aware(datetime.datetime.fromtimestamp(float(data['time'])), timezone=timezone.utc)
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        runs = Run.objects.all().filter(end_time__gte=from_time)
        result = []
        for run in runs:
            serializer = RunReportSerializer(run)
            result.append(serializer.data)
        return Response(result)
