from rest_framework.parsers import JSONParser
from .serializers import RunSerializer
from .models import Run
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class RunCreateView(APIView):
    parser_classes = (JSONParser,)

    @staticmethod
    def post(request):
        runs_json = JSONParser().parse(request)
        error_messages = []
        created_runs = []
        for run_json in runs_json:
            serializer = RunSerializer(data=run_json)
            if serializer.is_valid():
                run = serializer.save()
                created_runs.append(run.id)  # We will replace id by token
            else:
                error_messages.append(serializer.error_messages)
        return Response({'error_messages': error_messages,
                         'created_runs': created_runs}, status=status.HTTP_207_MULTI_STATUS)

    @staticmethod
    def get(request):
        data = JSONParser().parse(request)
        runs = Run.objects.all().query(end_time_gte=data['from_time'])
        return Response(runs)
