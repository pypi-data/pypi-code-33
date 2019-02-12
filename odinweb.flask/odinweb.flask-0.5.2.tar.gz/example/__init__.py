import odin

from flask import Flask
from odin.utils import getmeta, field_iter_items, field_iter

from odinweb import api, doc
from odinweb.data_structures import HttpResponse
from odinweb.flask import ApiBlueprint
from odinweb.cors import CORS
from odinweb.swagger import SwaggerSpec


class User(odin.Resource):
    """
    User resource
    """
    id = odin.IntegerField(key=True)
    username = odin.StringField()
    name = odin.StringField()
    email = odin.EmailField()
    role = odin.StringField(choices=('a', 'b', 'c'))


class UserSummary(odin.ResourceProxy):
    class Meta:
        resource = User
        include = ('id', 'username', 'name')
        readonly = ('id', 'username')


USERS = [
    User(1, 'pimpstar24', 'Bender', 'Rodreges', 'bender@ilovebender.com'),
    User(2, 'zoidberg', 'Zoidberg', '', 'zoidberg@freemail.web'),
    User(3, 'amylove79', 'Amy', 'Wong', 'awong79@marslink.web'),
]
USER_ID = len(USERS)


class UserApi(api.ResourceApi):
    resource = User
    tags = ['user']

    @doc.deprecated
    @api.collection(path='find', methods=api.Method.POST)
    def operation_test(self, request):
        pass

    @api.listing(resource=UserSummary)
    def get_user_list(self, request, offset, limit):
        return UserSummary.proxy(USERS[offset:offset+limit]), len(USERS)

    @api.action(path='stream')
    def get_user_stream(self, request):
        """
        Streamed user response.
        """
        def generate():
            yield '\t'.join(f.name for f in field_iter(User)) + '\n'

            for user in USERS:
                yield '\t'.join(str(v) for _, v in field_iter_items(user)) + '\n'

        return HttpResponse(generate(), headers={'Content-Type': 'text/plain'})

    @api.create(resource=UserSummary)
    def create_user(self, request, user):
        global USER_ID

        # Add user to list
        USER_ID += 1
        user.id = USER_ID
        USERS.append(user)

        return user

    @api.detail
    def get_user(self, request, id):
        """
        Get a user object
        """
        for user in USERS:
            if user.id == id:
                return user

        raise api.HttpError(api.HTTPStatus.NOT_FOUND)

    @api.update
    def update_user(self, request, user, id):
        return user

    @api.patch
    def patch_user(self, request, user, id):
        return user

    @api.delete
    def delete_user(self, request, id):
        for idx, user in enumerate(USERS):
            if user.id == id:
                USERS.remove(user)
                return

        raise api.HttpError(api.HTTPStatus.NOT_FOUND)


sample_api = api.ApiCollection(name='sample')


@sample_api.operation(path='foo/bar')
def sample(request):
    return {}


app = Flask(__name__)
app.register_blueprint(
    CORS(
        ApiBlueprint(
            api.ApiVersion(
                SwaggerSpec("Flask Example Swaggerspec", enable_ui=True),
                sample_api,
                UserApi(),
            ),
            middleware=[],
            debug_enabled=True,
        ),
        origins=['http://localhost:5000'],
        max_age=10,
    )
)


if __name__ == '__main__':
    app.run(debug=True)
