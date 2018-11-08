"""gee_bridge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^$', helloworld.views.index),
    url(r'^geemgr/api/v1/', include('api.urls')),
    # url(r'^maps/', include('gee_agent.urls'))
    # url(r'^geemgr/maps/', include('gee_agent.urls')),
    # url from mapclient
    # url(r'^', include('mapclient.urls')),
    # url from webmapping
    # url(r'^', include('webmapping.urls')),
]
