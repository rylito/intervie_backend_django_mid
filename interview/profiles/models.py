from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class UserProfile(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    email = models.EmailField(_("email address"), unique=True)
    avatar = models.ImageField()

    is_admin = models.BooleanField(_("admin"), default=False,
        help_text=_("Designates that this user is an admin.")
    )

