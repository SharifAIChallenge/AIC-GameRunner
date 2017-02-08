from django.contrib import admin

from api.models import IPBinding, Token

admin.site.register(IPBinding)
admin.site.register(Token)
