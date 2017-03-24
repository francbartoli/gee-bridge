from django.conf.urls import url
from django.contrib.auth import views as auth_views
from mapclient.views import *

urlpatterns = [
    url(r'^register/', CreateUserView.as_view()),
    url(r'^login/$', auth_views.login,
        {'template_name': 'login.html'}),
    url(r'^logout/$', auth_views.logout,
        {'next_page': '/'}),
    url(r'^webmap/$', MapView.as_view()),

    url(r'^$', HomeView.as_view())
]
