from django.contrib import admin

# Register your models here.
from bart.models import *

class CommandAdmin(admin.ModelAdmin):
    list_display = ("name", "api_cmd", "link", "formatter")
    list_display_links = ("name", "api_cmd")

class ParameterAdmin(admin.ModelAdmin):
    list_display = ("name", "param_type")
    ordering = ("order",)

class LineAdmin(admin.ModelAdmin):
    list_display = ("name",)

class StationAdmin(admin.ModelAdmin):
    list_display = ("key", "name")

class StationAliasAdmin(admin.ModelAdmin):
    list_display = ("alias",)

admin.site.register(Command, CommandAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(StationAlias, StationAliasAdmin)