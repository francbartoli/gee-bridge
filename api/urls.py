from api import views as api_views
from api.views import api_schema_view as api_schema_view
from api.views import swagger_schema_view as schema_swagger_view
from django.conf.urls import include, url
from djoser import views as djoser_views
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework_jwt import views as jwt_views
# from rest_framework_swagger.views import get_swagger_view

schema_view = get_schema_view(title='Rasterbucket API')
# swagger_view = get_swagger_view(title='Rasterbucket API')

urlpatterns = [
    url(r'^livedoc/swagger(?P<format>.json|.yaml)$',
        api_schema_view.without_ui(cache_timeout=None),
        name='schema-json'),
    url(r'^livedoc/swagger/$',
        api_schema_view.with_ui('swagger', cache_timeout=None),
        name='schema-swagger-ui'),
    url(r'^livedoc/redoc/$',
        api_schema_view.with_ui('redoc', cache_timeout=None),
        name='schema-redoc'),

    # Security
    # using JSON web token
    url(r'^security/restauth/',
        include('rest_auth.urls')),
    url(r'^security/restauth/verify/$', 
        jwt_views.verify_jwt_token),
    # using social auth
    url(r'^security/restauth/',
        include('rest_social.urls')),
    # using registration
    url(r'^security/restauth/registration/',
        include('rest_auth.registration.urls')),
    url(r'^security/djoser/',
        include('djoser.urls')),

    # Process
    url(r'^processes/$',
        # api_views.process_list, # FBV
        api_views.ProcessList.as_view(),
        name='process-list'),
    url(r'^processes/(?P<id>[^/]+)$',
        # api_views.process_detail, #FBV
        api_views.ProcessDetail.as_view(),
        name='process-detail'),

    # Rasterbucket
    url(r'^rasterbuckets/$',
        api_views.RasterbucketCreateView.as_view(),
        name='api.rasterbuckets'),
    url(r'^rasterbuckets/(?P<pk>[0-9]+)/$',
        api_views.RasterbucketDetailsView.as_view(),
        name="api.rasterbuckets.details"),

    url(r'^rasterbuckets/(?P<pk>[0-9]+)/services/$',
        api_views.RasterbucketServiceCreateView.as_view(),
        name="api.rasterbuckets.services"),
    url(r'^rasterbuckets/(?P<pk>[0-9]+)/services/(?P<pk_service>[0-9]+)/$',
        api_views.RasterbucketServiceDetailView.as_view(),
        name="api.rasterbuckets.services.details"),

    url(r'^rasterbuckets/(?P<pk>[0-9]+)/\
services/(?P<pk_service>[0-9]+)/maps/$',
        api_views.GEEMapServiceCreateView.as_view(),
        name="api.rasterbuckets.services.geemapservices.create"),
    url(r'^rasterbuckets/(?P<pk>[0-9]+)/\
services/(?P<pk_service>[0-9]+)/maps/(?P<pk_map>[0-9]+)/$',
        api_views.MapServiceDetailView.as_view(),
        name="api.rasterbuckets.services.mapservice.detail")
]
