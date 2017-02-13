from rest_framework.schemas import SchemaGenerator


class CustomFieldSchemaGenerator(SchemaGenerator):

    def get_serializer_fields(self, path, method, view):
        method_name = getattr(view, 'action', method.lower())
        method_func = getattr(view, method_name, None)
        fields = getattr(method_func, 'coreapi_fields', [])
        if getattr(method_func, 'use_serializer', True):
            fields = fields + \
                     super(CustomFieldSchemaGenerator, self).get_serializer_fields(path, method, view)
        return fields
