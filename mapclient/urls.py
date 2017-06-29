from django.conf.urls import url
from django.contrib.auth import views as auth_views
from mapclient.views import *
from rest_framework.routers import DefaultRouter

urlpatterns = [
    url(r'^register/', CreateUserView.as_view()),
    url(r'^login/$', auth_views.login,
        {'template_name': 'login.html'}),
    url(r'^logout/$', auth_views.logout,
        {'next_page': '/'}),
    url(r'^webmap/$', MapView.as_view()),

    url(r'^$', HomeView.as_view())
]

urlpatterns += [
    url(r'^currentuser/', CurrentUserView.as_view()),
]
router = DefaultRouter()
router.register(r'processes', UserProcessViewSet, 'map_processes')
urlpatterns += router.urls
