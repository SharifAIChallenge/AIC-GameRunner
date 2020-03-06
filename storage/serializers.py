from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'created_at', 'owner', 'file',)
        read_only_fields = ('id', 'created_at', 'owner', )


class FileDirectSerializer(serializers.ModelSerializer):
    user_token = serializers.CharField()
    language = serializers.CharField()

    class Meta:
        model = File
        fields = ('id', 'created_at', 'owner', 'file', 'user_token', 'language')
        read_only_fields = ('id', 'created_at', 'owner', )


class FileUrlSerializer(serializers.Serializer):
    url = serializers.URLField()

