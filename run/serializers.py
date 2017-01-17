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
    file_path_set = FilePathSerializer(many=True)

    class Meta:
        model = Run
        fields = (
            # 'game',
            'file_path_set',)

    def create(self, validated_data):
        run = Run(file_path_set=validated_data['file_path_set'])
        run.save()
        return run
