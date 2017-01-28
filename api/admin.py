from django.contrib import admin

# Register your models here.
from api.models import IP, Token

admin.site.register(IP)
admin.site.register(Token)