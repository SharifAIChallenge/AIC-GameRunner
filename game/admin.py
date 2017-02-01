from django.contrib import admin

# Register your models here.
from game.models import Competition, Game, Team, CompetitionLanguage, DockerContainer

admin.site.register(Competition)
admin.site.register(Game)
admin.site.register(Team)
admin.site.register(CompetitionLanguage)
admin.site.register(DockerContainer)