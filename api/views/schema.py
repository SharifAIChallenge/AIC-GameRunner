from rest_framework import renderers, response
from rest_framework.views import APIView

from api.schemas import CustomFieldSchemaGenerator

generator = CustomFieldSchemaGenerator(title='API Schema')


class SchemaView(APIView):
    renderer_classes = [renderers.CoreJSONRenderer, ]
    exclude_from_schema = True

    def get(self, request):
        schema = generator.get_schema(request)
        return response.Response(schema)
