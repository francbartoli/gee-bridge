from django.contrib import admin
from django.forms import ModelForm
from api.models import Process
from prettyjson import PrettyJSONWidget
from django.contrib.postgres.fields import JSONField
# Register your models here.


class JsonForm(ModelForm):
    class Meta:
        model = Process
        fields = '__all__'
        widgets = {
            'type': PrettyJSONWidget(),
        }


class ProcessAdmin(admin.ModelAdmin):
    form = JsonForm

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }

    list_display = (
        'id', 'name', 'type', 'owner', 'aoi',
        'toi', 'input_data', 'output_data'
    )


admin.site.register(Process, ProcessAdmin)
