from rest_framework import serializers
from rest_framework.parsers import JSONParser
from .models import Run
from .models import FilePath
from storage.models import File
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


class FilePathSetSerializerField(serializers.Field):
    def to_representation(self, value):
        raise NotImplemented()

    def to_internal_value(self, data):
        internal_value = []
        if not isinstance(data, dict):
            raise serializers.ValidationError('files data must be a dictionary.')
        for file_definition in data:
            if 'id' not in data[file_definition]:
                raise serializers.ValidationError('file id not provided.')
            if 'is_input' not in data[file_definition]:
                raise serializers.ValidationError('file id not provided.')
            internal_value.append(FilePath(file=File.objects.get(id=data[file_definition]['id']),
                                           is_input=data[file_definition]['is_input']))
        return internal_value
        #
        # def to_representation(self, value):
        #     file_paths = []
        #     if not isinstance(value, FilePath):
        #         raise TypeError()
        #     for file_path in self.instance:
        #         file_paths.append(FilePathSerializer(file_path).data)


class RunCreateSerializer(serializers.Serializer):
    files = FilePathSetSerializerField()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        run = Run()
        run.save()
        for file_path in validated_data['files']:
            file_path.run = run
            file_path.save()
        run.file_path_set = validated_data['files']
        run.save()
        return run
