from allauth.socialaccount.providers.facebook.views import (
    FacebookOAuth2Adapter
)
from allauth.socialaccount.providers.google.views import (
    GoogleOAuth2Adapter
)
from allauth.socialaccount.providers.github.views import (
    GitHubOAuth2Adapter
)
from rest_auth.registration.views import (
    SocialLoginView,
    SocialConnectView
)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter

class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter

class GitHubConnect(SocialConnectView):
    adapter_class = GitHubOAuth2Adapter