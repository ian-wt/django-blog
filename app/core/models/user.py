import zoneinfo

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.utils import timezone

TIMEZONES = tuple(zip(
    zoneinfo.available_timezones(),
    zoneinfo.available_timezones()
))


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('User must provide email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('User type created with this method must be '
                             'superuser')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin "
                    "site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        creation = self._state.adding
        super().save(*args, **kwargs)
        if creation: UserProfile.objects.create(user=self)

    def get_full_name(self):
        """
        Return a concatenation of the first_name and last_name fields separated
           by a space.
        """
        return f'{self.first_name} {self.last_name}'

    def get_user_initials(self):
        """
        Return the uppercase of the first characters of the first_name and
           last_name fields.
        """
        return '{}{}'.format(
            self.first_name[0].upper(),
            self.last_name[0].upper()
        )


class UserProfile(models.Model):
    """
    Model for storing additional information pertaining to the user.
    """
    user = models.OneToOneField(
        'core.User',
        on_delete=models.CASCADE,
        related_name='user_profile'
    )
    timezone = models.CharField(
        max_length=32,
        choices=TIMEZONES,
        default='UTC'
    )

    objects = models.Manager()

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f"{self.user.first_name} {self.user.last_name}'s Profile"
