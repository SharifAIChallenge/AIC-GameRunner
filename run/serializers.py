from rest_framework import serializers
from .models import Run
from .models import FilePath


class FilePathSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilePath
        fields = ('file', 'path',)


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = (
            # 'token', 'game',
            'id', 'request_time', 'start_time', 'end_time', 'owner', 'input_file_paths', 'output_file_paths', 'log',)
        read_only_fields = (
            # 'token'
            'id', 'request_time', 'start_time', 'end_time', 'owner', 'log',)
