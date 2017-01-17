from rest_framework import serializers
from .models import Run
from .models import FilePath
from storage.serializers import FileSerializer


class FilePathSerializer(serializers.ModelSerializer):
    file = FileSerializer(many=False)

    # definition = FileDefinitionSerializer()

    class Meta:
        model = FilePath
        fields = ('file',
                  # 'definition',
                  )


class RunReportSerializer(serializers.ModelSerializer):
    file_path_set = FilePathSerializer(many=True, read_only=True)

    class Meta:
        model = Run
        fields = (
            # 'game',
            'id', 'status', 'end_time', 'log', 'file_path_set')
        read_only_fields = fields


class RunCreateSerializer(serializers.ModelSerializer):
    output_file_paths = FilePathSerializer(many=True)
    input_file_paths = FilePathSerializer(many=True)

    class Meta:
        model = Run
        fields = (
            # 'game',
            'id', 'file_path_set',)
