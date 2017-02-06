from django.contrib import admin

# Register your models here.
from api.models import IPBinding, Token

admin.site.register(IPBinding)
admin.site.register(Token)