from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CreateView

urlpatterns = {
    url(r'^rasterbuckets/$', CreateView.as_view(),
        name='api.rasterbuckets'),
}

urlpatterns = format_suffix_patterns(urlpatterns)
