from django.contrib import admin

# Register your models here.
from game.models import *

admin.site.register(Game)
admin.site.register(Operation)
admin.site.register(OperationParameter)
admin.site.register(OperationResource)