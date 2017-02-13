from django.contrib import admin

# Register your models here.
from game.models import *


class OperationParameterInlineAdmin(admin.TabularInline):
    model = OperationParameter


class OperationAdmin(admin.ModelAdmin):
    inlines = (OperationParameterInlineAdmin, )

admin.site.register(Game)
admin.site.register(Operation, OperationAdmin)
admin.site.register(OperationParameter)
admin.site.register(OperationResource)
