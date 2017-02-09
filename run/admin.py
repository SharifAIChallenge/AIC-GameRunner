from django.contrib import admin
from .models import Run, ParameterValue

# Register your models here.

class RunAdmin(admin.ModelAdmin):
    actions = ['execute']
    
    def execute(self, request, queryset):
        for run in queryset:
            run.compile_compose_file()

admin.site.register(Run, RunAdmin)
admin.site.register(ParameterValue)
