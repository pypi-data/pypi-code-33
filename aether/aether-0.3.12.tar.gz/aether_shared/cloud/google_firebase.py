import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin.auth import AuthError
from firebase_admin import firestore


#######################################################################################################################
#
# The API uses Google Firebase for authentication. Once a user registers on Google Firebase, the API uses their UID
# as token for authentication. The UID retrieves the user email address and name for any additional processing.
#
#######################################################################################################################

class google_firebase(object):

    _certificate_filename = 'certificates/aether-185123-firebase-adminsdk-mh9uu-ee43070fad.json'

    def __init__(self):
        try:
            print("Initializing Firebase Authentication.")
            self._credentials = credentials.Certificate(self._certificate_filename)
            self._app = firebase_admin.initialize_app(self._credentials, options=dict(databaseURL="https://test.firebase.localhost:5002/"))
            self._firestore_client = firestore.client()
            print("Firebase Authentication successfully initialized.")
        except Exception, e:
            print("ERROR: Firebase Authentication failed, error: {}".format(e))

    def firestore_client(self):
        return self._firestore_client

    def is_authorized_user(self, uid, return_user_data=False):
        try:
            user = auth.get_user(uid)
            print 'Successfully fetched user data: {} {} {}'.format(user.uid, user.email, user.display_name)
            if return_user_data:
                return user
            else:
                return True
        except AuthError, e:
            print("ERROR: Authentication error: Either UID Token does not exist or an error occurred while retrieving.")
            print("ERROR: {}".format(e))
            if return_user_data:
                return None
            else:
                return False

    def user_exists(self, email_or_uuid, is_email=True):
        try:
            if is_email:
                user = self.get_user_by_email(email_or_uuid)
            else:
                user = self.get_user(email_or_uuid)
        except AuthError, e:
            if e.code != 'USER_NOT_FOUND_ERROR':
                print("ERROR: Unexpected error, cannot determine whether user exists: {}".format(e))
            return False
        return True

    def get_user_by_email(self, email):
        return auth.get_user_by_email(email)

    def get_user(self, uid):
        return self.is_authorized_user(uid, return_user_data=True)

    def user_record_as_dict(self, user_record):
        return dict(
            email=user_record.email,
            phone_number=user_record.phone_number,
            display_name=user_record.display_name,
            email_verified=user_record.email_verified,
            uuid=user_record.uid,
            photo_url=user_record.photo_url,
        )

    def create_new_user(self, email, password, display_name):
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
        )
        return user
