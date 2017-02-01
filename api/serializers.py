from rest_framework import serializers
from rest_framework.parsers import JSONParser
from run.models import Run
from run.models import ParameterValue
from storage.models import File
from storage.serializers import FileSerializer


# class FilePathSerializer(serializers.ModelSerializer):
#     file = FileSerializer(many=False)
#
#     # definition = FileDefinitionSerializer()
#
#     class Meta:
#         model = FilePath
#         fields = ('file',
#                   # 'definition',
#                   )

class ParameterValueSetSerializerField(serializers.Field):
    def to_representation(self, value):
        result = {}
        for parameter_value in value:
            # todo serialize file definition
            result[parameter_value.parameter.name] = parameter_value._value
        return result

    def to_internal_value(self, data):
        internal_value = []
        if not isinstance(data, dict):
            raise serializers.ValidationError('parameters data must be a dictionary.')
            # todo add this
            # for parameter in data:
            # internal_value.append(
            #     ParameterValue(parameter=Parameter.objects.get(name=parameter), _value=data[parameter],
            #                    is_input=True))
        return internal_value


class RunReportSerializer(serializers.ModelSerializer):
    parameters = ParameterValueSetSerializerField(read_only=True)

    class Meta:
        model = Run
        fields = (
            # 'game',
            'id', 'status', 'end_time', 'log', 'parameters')
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['parameters'] = ParameterValueSetSerializerField().to_representation(instance.parameter_set.all())
        return data


class RunCreateSerializer(serializers.Serializer):
    files = ParameterValueSetSerializerField()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        run = Run()
        run.save()
        for parameter_value in validated_data['parameters']:
            parameter_value.run = run
            parameter_value.save()
        run.parameter_set = validated_data['parameters']
        run.save()
        return run
