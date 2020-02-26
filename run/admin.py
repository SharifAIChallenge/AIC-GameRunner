from django.contrib import admin
from .models import Run, ParameterValue

# Register your models here.

class ParameterValueInlineAdmin(admin.TabularInline):
    model = ParameterValue


class RunAdmin(admin.ModelAdmin):
    actions = ['execute']
    inlines= (ParameterValueInlineAdmin, )
    
    def execute(self, request, queryset):
        for run in queryset:
            run.recompile()

admin.site.register(Run, RunAdmin)
admin.site.register(ParameterValue)
