from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)
from firebase_sdkadm import firebase_decode_handler

class FirebaseAuthentication(BaseAuthentication):
    """Simple Firebase based authentication.

    Authenticate the user and get its additional info from Firebase.
    Clients should authenticate by passing the Token Id in the "Authorization"
    HTTP header, prepended with the string "Bearer " and verified by the Firebase admin.
    For example:
        Authorization: Bearer 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Bearer'
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

        if not fb_auth or fb_auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = fb_auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

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
            print (
                "The retrieved user from Firebase is {user}".format(
                    user
                )
            )
        except auth.AuthError as e:
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
        return self.keyword

    # def authenticate(self, request):
    #     """Actual authentication happens here."""
    #     token = request.META.get('HTTP_TOKENID')
    #     if token:
    #         try:
    #             firebase_user = auth.verify_id_token(token)
    #         except ValueError:
    #             return None
    #         if not firebase_user:
    #             return None

    #         user_id = firebase_user.get('user_id')
    #         try:
    #             user = User.objects.get(id=user_id)
    #             print(user)
    #         except User.DoesNotExist:
    #             raise exceptions.AuthenticationFailed('No such user')
    #         return (user, None)
    #     else:
    #         # no token provided
    #         return None