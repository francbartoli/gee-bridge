from django.conf.urls import include, url
from rest_social.social.provider import (
    FacebookLogin,
    FacebookConnect,
    GoogleLogin,
    GoogleConnect,
    GitHubLogin,
    GitHubConnect
)
from rest_auth.registration.views import (
    SocialAccountListView,
    SocialAccountDisconnectView
)


urlpatterns = [
    url(r'^social/facebook/$',
        FacebookLogin.as_view(),
        name='fb_login'),
    url(r'^social/google/$',
        GoogleLogin.as_view(),
        name='google_login'),
    url(r'^social/github/$',
        GitHubLogin.as_view(),
        name='github_login'),
    url(r'^social/facebook/connect/$',
        FacebookConnect.as_view(),
        name='fb_connect'),
    url(r'^social/google/connect/$',
        GoogleConnect.as_view(),
        name='google_connect'),
    url(r'^social/github/connect/$',
        GitHubConnect.as_view(),
        name='github_connect'),
    url(
        r'^social/socialaccounts/$',
        SocialAccountListView.as_view(),
        name='social_account_list'
    ),
    url(
        r'^social/socialaccounts/(?P<pk>\d+)/disconnect/$',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect'
    )
]