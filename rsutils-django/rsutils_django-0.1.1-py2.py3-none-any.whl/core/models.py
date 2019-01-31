from uuid import uuid4
from safedelete.models import SafeDeleteModel
from django.contrib.auth.models import AbstractUser
from django.db.models import DateTimeField, UUIDField


class RSModel(SafeDeleteModel):
    updated_at = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)
    id = UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class RSUser(AbstractUser, RSModel):

    REQUIRED_FIELDS = ['email', 'username']

    class Meta:
        abstract = True
