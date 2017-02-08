from django.contrib import admin

from docker_registry.models import DockerFile, Resource


class DockerFileAdmin(admin.ModelAdmin):
    actions = ['build_and_push']

    def build_and_push(self, request, queryset):
        for dockerfile in queryset:
            dockerfile.build_and_push()

    build_and_push.short_description = "Build image and push to image registry"


admin.site.register(DockerFile, DockerFileAdmin)
admin.site.register(Resource)
