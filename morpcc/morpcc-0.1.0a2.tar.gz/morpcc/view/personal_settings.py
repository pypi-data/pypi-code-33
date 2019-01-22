import morepath
import colander
import deform
import deform.widget
from morpfw.authn.pas.user.path import get_user_collection
from ..crud.tempstore import FSBlobFileUploadTempStore
import morpfw.authn.pas.exc
from ..app import App, SQLAuthApp
from ..root import Root
from .. import permission
from ..util import dataclass_to_colander


class UserInfoSchema(colander.MappingSchema):
    username = colander.SchemaNode(
        colander.String(),
        oid='userinfo-username',
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'))
    email = colander.SchemaNode(
        colander.String(),
        oid='userinfo-email',
        validator=colander.Email(msg="Invalid e-mail address"))
    state = colander.SchemaNode(
        colander.String(),
        oid='userinfo-state',
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'))
    created = colander.SchemaNode(
        colander.DateTime(),
        oid='userinfo-created',
        missing=None,
        widget=deform.widget.DateTimeInputWidget(template='readonly/datetimeinput'))


class PasswordSchema(colander.MappingSchema):
    password_current = colander.SchemaNode(colander.String(),
                                           oid='password-current',
                                           title="Current password",
                                           widget=deform.widget.PasswordWidget(),
                                           missing='')

    password = colander.SchemaNode(colander.String(),
                                   oid='password-new',
                                   title="New password",
                                   widget=deform.widget.PasswordWidget(),
                                   missing='',
                                   validator=colander.Length(min=8))
    password_confirm = colander.SchemaNode(colander.String(),
                                           oid='password-confirm',
                                           widget=deform.widget.PasswordWidget(),
                                           title="Confirm new password",
                                           missing='')

    def validator(self, node: "PasswordSchema", appstruct: dict):
        if appstruct['password'] != appstruct['password_confirm']:
            raise colander.Invalid(node['password'], "Password does not match")


def userinfo_form(request) -> deform.Form:
    return deform.Form(UserInfoSchema(), buttons=('Submit',),
                       formid='userinfo-form')


def attributes_form(context, request) -> deform.Form:
    schema = context.xattrprovider().schema
    return deform.Form(dataclass_to_colander(schema)(), buttons=('Submit',), formid='personalinfo-form')


def password_form(request) -> deform.Form:
    return deform.Form(PasswordSchema(), buttons=('Change password',),
                       formid='password-form')


def upload_form(request) -> deform.Form:
    class FileUpload(colander.Schema):
        upload = colander.SchemaNode(deform.FileData(),
                                     widget=deform.widget.FileUploadWidget(
                                     FSBlobFileUploadTempStore(request, '/tmp/tempstore')),
                                     oid='file-upload')
    return deform.Form(FileUpload(), buttons=('Upload', ), formid='upload-form')


@App.html(model=Root, name='personal-settings', template="master/personal-settings.pt",
          permission=permission.EditOwnProfile)
def profile(context, request: morepath.Request):
    userid = request.identity.userid
    newreq = request.get_authn_request()
    usercol = get_user_collection(newreq)
    user = usercol.get_by_userid(userid)
    has_photo = user.get_blob('profile-photo')
    return {
        'page_title': 'Profile',
        'profile_photo': newreq.link(user, '+blobs?field=profile-photo') if has_photo else None,
        'forms': [{
            'form_title': 'Personal Information',
            'form': attributes_form(user, request),
            'readonly': False,
            'form_data': user.data['xattrs']
        }, {
            'form_title': 'User Information',
            'form': userinfo_form(request),
            'readonly': False,
            'form_data': user.data.as_dict()
        },
            {
            'form_title': 'Password',
            'form': password_form(request),
            'readonly': False,
        }]
    }


@App.html(model=Root, name='personal-settings', request_method='POST',
          template='master/personal-settings.pt', permission=permission.EditOwnProfile)
def process_profile(context, request):
    userinfo_f = userinfo_form(request)
    password_f = password_form(request)
    controls = list(request.POST.items())
    controls_dict = dict(controls)
    active_form = controls_dict['__formid__']

    userid = request.identity.userid
    newreq = request.get_authn_request()
    usercol = get_user_collection(newreq)
    user = usercol.get_by_userid(userid)

    attributes_f = attributes_form(user, request)

    failed = False
    if active_form == 'userinfo-form':
        try:
            data = userinfo_f.validate(controls)
        except deform.ValidationFailure as e:
            failed = True
            userinfo_f = e
            userdata = userinfo_f.field.schema.serialize(
                user.data.as_dict())
            for k in userdata.keys():
                if userinfo_f.cstruct[k] is not colander.null:
                    userdata[k] = userinfo_f.cstruct[k]
            userinfo_f.field.cstruct = userdata

        if not failed:
            updatedata = {}
            for f in ['email']:
                updatedata[f] = data[f]
            user.update(updatedata)

        if not failed:
            request.notify('success', 'Profile updated',
                           'Your profile have been successfully updated')
            return morepath.redirect(request.url)
    elif active_form == 'password-form':
        try:
            data = password_f.validate(controls)
        except deform.ValidationFailure as e:
            failed = True
            password_f = e

        if not failed:
            if not user.validate(data['password_current']):
                exc = colander.Invalid(password_f, 'Invalid password')
                password_f.widget.handle_error(password_f, exc)
                failed = True

        if not failed:
            try:
                user.change_password(
                    data['password_current'], data['password'])
            except morpfw.authn.pas.exc.InvalidPasswordError as e:
                exc = colander.Invalid(password_f, 'Invalid password')
                password_f.widget.handle_error(password_f, exc)
                failed = True

        if not failed:
            request.notify('success', 'Password changed',
                           'Your password have been successfully changed')
            return morepath.redirect(request.url)
    elif active_form == 'personalinfo-form':
        try:
            data = attributes_f.validate(controls)
        except deform.ValidationFailure as e:
            failed = True
            attributes_f = e

        if not failed:
            xattrprovider = user.xattrprovider()
            xattrprovider.update(data)
            request.notify('success', 'Profile updated',
                           'Your profile have been successfully updated')
            return morepath.redirect(request.url)

    else:
        request.notify('error', 'Unknown form',
                       'Invalid form identifier was supplied')

        return morepath.redirect(request.url)

    has_photo = user.get_blob('profile-photo')
    return {
        'page_title': 'Personal Settings',
        'profile_photo': newreq.link(user, '+blobs?field=profile-photo') if has_photo else None,
        'forms': [
            {
                'form_title': 'Personal Information',
                'form': attributes_f,
                'readonly': False,
                'form_data': user['xattrs'] if active_form != 'personalinfo-form' else None
            },
            {
                'form_title': 'User Information',
                'form': userinfo_f,
                'readonly': False,
                'form_data': user.data.as_dict() if active_form != 'userinfo-form' else None
            }, {
                'form_title': 'Password',
                'form': password_f,
                'readonly': False,
            }]
    }


@App.html(model=Root, name='upload-profile-photo', permission=permission.EditOwnProfile,
          template='master/simple-form.pt')
def upload_profile_photo(context, request):
    return {
        'page_title': 'Upload image',
        'form_title': 'Upload',
        'form': upload_form(request)
    }


@App.html(model=Root, name='upload-profile-photo', permission=permission.EditOwnProfile,
          template='master/simple-form.pt', request_method='POST')
def process_upload_profile_photo(context, request):
    form = upload_form(request)
    controls = list(request.POST.items())

    failed = False
    data = {}
    try:
        data = form.validate(controls)
    except deform.ValidationFailure as e:
        failed = True
        form = e

    if not failed:
        userid = request.identity.userid
        newreq = request.get_authn_request()
        usercol = get_user_collection(newreq)
        user = usercol.get_by_userid(userid)
        filedata = data['upload']
        user.put_blob(
            'profile-photo', filedata['fp'], filename=filedata['filename'],
            mimetype=filedata['mimetype'])
        request.notify('success', 'Profile photo updated',
                       'Successfully updated profile photo')
        return morepath.redirect(request.relative_url('/personal-settings'))

    return {
        'page_title': 'Upload image',
        'form_title': 'Upload',
        'form': form,
        'form_data': data if not failed else None
    }
