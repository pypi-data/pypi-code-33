from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.forms import EmailField, CharField
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserAddWithoutPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "birthday", "email", "phone")
        field_classes = {"email": EmailField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update(
                {"autofocus": True}
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("name", "birthday", "email", "phone")},
        ),
    )
    add_form = UserAddWithoutPasswordForm

    list_display = (
        "is_active",
        "name",
        "birthday",
        "email",
        "phone",
        "is_superuser",
        "is_staff",
    )
    list_display_links = ("name", "email")
    ordering = None

    fieldsets = [
        (None, {"fields": ("name", "birthday", "email", "phone", "password")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
    ]


#    change_form_template = "admin/user_changeform.html"

#    def response_change(self, request, obj):
#        if "_generate_auth_token" in request.POST:
#            token_suffix = sesame_utils.get_query_string(obj)
#            path = reverse("list-shares") + token_suffix
#            days_valid = settings.SESAME_MAX_AGE / (24 * 3600)
#            url = request.build_absolute_uri(path)
#            messages.success(
#                request,
#                mark_safe(
#                    f'Login-URL (gültig für {days_valid} Tage): <a href="{url}">{url}</a>'
#                ),
#            )
#        return super().response_change(request, obj)
