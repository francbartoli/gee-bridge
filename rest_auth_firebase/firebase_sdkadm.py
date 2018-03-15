import firebase_admin
from firebase_admin import credentials, auth
from gee_bridge import settings


credential = settings.FIREBASE_CREDENTIALS
firebase_admin.initialize_app(credential)


def firebase_decode_handler(id_token):
    # Verify the ID token while checking if the token is revoked by
    # passing check_revoked=True.
    decoded_token = auth.verify_id_token(id_token, check_revoked=True)
    uid = decoded_token['uid']
    print("User={0}".format(uid))
    return uid