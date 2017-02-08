from django.contrib import admin

from game.models import *

admin.site.register(Game)
admin.site.register(Operation)
admin.site.register(OperationParameter)
admin.site.register(OperationResource)
