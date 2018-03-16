from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)
from rest_auth_firebase.firebase_sdkadm import firebase_decode_handler
import firebase_admin
from firebase_admin.auth import AuthError
import sys

class FirebaseAuthentication(BaseAuthentication):
    """Simple Firebase based authentication.

    Authenticate the user and get its additional info from Firebase.
    Clients should authenticate by passing the Token Id in the "Authorization"
    HTTP header, prepended with the string "Bearer " and verified by the Firebase admin.
    For example:
        Authorization: Bearer 401f7ac837da42b97f613d789819ff93537bee6a
    """

    www_authenticate_realm = 'api'
    FIREBASE_AUTH_HEADER_PREFIX = 'Bearer'
    keyword = FIREBASE_AUTH_HEADER_PREFIX
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.
    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        
        fb_auth = get_authorization_header(request).split()
        import ipdb; ipdb.set_trace()

        if not fb_auth or fb_auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(fb_auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(fb_auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = fb_auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)
        except ValueError:
            msg = _('Invalid token header. Token is expired.')
            raise exceptions.AuthenticationFailed(msg)
        username = self.authenticate_credentials(token).encode()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
             user = User(username=username)
             user.save()

        return (user, token)

    # TODO do something similar if the user has to be registered locally
    # def authenticate_credentials(self, key):
    #     model = self.get_model()
    #     try:
    #         token = model.objects.select_related('user').get(key=key)
    #     except model.DoesNotExist:
    #         raise exceptions.AuthenticationFailed(_('Invalid token.'))

    #     if not token.user.is_active:
    #         raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

    #     return (token.user, token)

    def authenticate_credentials(self, key):

        try:
            user = firebase_decode_handler(key)
            print(
                "The retrieved user from Firebase is {0}".format(
                    user
                )
            )
        except AuthError as e:
            if e.code == 'ID_TOKEN_REVOKED':
                # Token revoked, inform the user to reauthenticate or signOut().
                raise exceptions.AuthenticationFailed(_(
                    'User token is revoked. Please authenticate again'
                ))
            else:
                # Token is invalid
                raise exceptions.AuthenticationFailed(_('Invalid token.'))
        
        return user


    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(
            self.FIREBASE_AUTH_HEADER_PREFIX,
            self.www_authenticate_realm
        )
