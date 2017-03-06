from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CreateView, DetailsView

urlpatterns = {
    url(r'^auth/', include('rest_framework.urls',
        namespace='rest_framework')),
    url(r'^rasterbuckets/$', CreateView.as_view(),
        name='api.rasterbuckets'),
    url(r'^rasterbuckets/(?P<pk>[0-9]+)/$',
        DetailsView.as_view(), name="details"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
