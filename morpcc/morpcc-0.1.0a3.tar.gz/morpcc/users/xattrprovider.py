import morpfw
from morpfw.authn.pas.user.model import UserModel
from morpfw.crud.xattrprovider import FieldXattrProvider
from ..app import App, SQLAuthApp
from dataclasses import dataclass
import typing


@dataclass
class UserXattrSchema(object):

    firstname: typing.Optional[str] = None
    lastname: typing.Optional[str] = None
    displayname: typing.Optional[str] = None
    address: typing.Optional[str] = None


class UserXattrProvider(FieldXattrProvider):

    schema = UserXattrSchema


@SQLAuthApp.xattrprovider(model=UserModel)
def get_xattr_provider(context):
    return UserXattrProvider(context)
