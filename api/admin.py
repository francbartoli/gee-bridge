from django.contrib import admin
from api.models import Process
# Register your models here.


class ProcessAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'type', 'owner', 'aoi',
        'toi', 'input_data', 'output_data'
    )


admin.site.register(Process, ProcessAdmin)
