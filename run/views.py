from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from .serializers import RunSerializer
from .models import Run
from rest_framework.response import Response


@api_view(http_method_names=['POST'])
def run(request):
    runs_json = JSONParser().parse(request)
    data_with_error = []
    for run_json in runs_json:
        serializer = RunSerializer(data=run_json)
        if serializer.is_valid():
            serializer.save()
        else:
            data_with_error.append(run_json)
    return Response({'data_with_error': data_with_error})


@api_view(http_method_names=['GET'])
def report(request):
    data = JSONParser().parse(request)
    runs = Run.objects.all().query(end_time_gte=data['from_time'])
    return Response(runs)
