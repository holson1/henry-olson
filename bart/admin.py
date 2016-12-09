from django.contrib import admin

# Register your models here.
from bart.models import *

class CommandAdmin(admin.ModelAdmin):
    list_display = ("name", "api_cmd", "link", "parser")

class ParameterAdmin(admin.ModelAdmin):
    list_display = ("name", "param_type")

admin.site.register(Command, CommandAdmin)
admin.site.register(Parameter, ParameterAdmin)