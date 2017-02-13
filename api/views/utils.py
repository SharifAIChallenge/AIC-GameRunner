import coreapi


def define_coreapi_field(*args, **kwargs):
    def wrapper(func):
        func.coreapi_fields = getattr(func, "coreapi_fields", [])
        func.coreapi_fields.append(coreapi.Field(*args, **kwargs))
        return func
    return wrapper