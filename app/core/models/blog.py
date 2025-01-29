import os
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError


# noinspection PyUnusedLocal
def cover_image_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('article-cover-images', filename)


class PostAuthor(models.Model):
    """
    Through table for Post Model.

    Use through table to associate additional data like 'main' /
        'contributing' author, etc.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey('core.Post', on_delete=models.CASCADE)


class Post(models.Model):
    """
    Blog Post Model.
    """

    # TODO: Add a 'tags' model relationship / functionality

    title = models.CharField(
        max_length=60,
        help_text=_('max length 60 characters')
    )
    description = models.CharField(
        max_length=255,
        help_text=_('recommended length 160 charaters (max 255)'),
        blank=True  # require to publish
    )
    body = models.TextField(
        blank=True  # require to publish
    )
    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through=PostAuthor
    )
    # TODO: Handle image resizing
    cover_image = models.ImageField(
        upload_to=cover_image_file_path,
        blank=True,  # require to publish
        null=True
    )
    cover_image_alt = models.CharField(
        max_length=255,
        blank=True,  # require to publish
        null=True
    )
    meta_title = models.CharField(
        max_length=60,
        help_text=_('title is used if blank (max 60 characters)'),
        blank=True
    )
    meta_description = models.CharField(
        max_length=255,
        help_text=_('description is used if blank (keep below 160, max 255)'),
        blank=True
    )
    slug = models.SlugField(
        db_index=False,
        max_length=100,
        blank=True  # require to publish
    )
    created_at = models.DateTimeField(default=timezone.now)
    # use updated_at to communicate a 'last update' to the viewer rather than
    #   a strict, every time the model is updated
    updated_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    # use timestamp for last mod
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # pre-save
        # creation = self._state.adding
        self.timestamp = timezone.now()
        self.full_clean()

        super().save(*args, **kwargs)

    def clean(self):
        # validate fields required for publish
        if self.published_at:
            errors = {}
            required_fields = [
                'description',
                'body',
                'cover_image',
                'cover_image_alt',
            ]
            for field in required_fields:
                if not getattr(self, field):
                    errors[field] = _(f'{field.replace("_", " ").title()} '
                                      f'is required to publish.')
            if errors:
                raise ValidationError(errors)

        # validate updated > published
        if self.published_at and self.updated_at \
            and (self.published_at >= self.updated_at):
            raise ValidationError(_(f'Update {self.updated_at} cannot occur'
                                    f'before Puplish {self.created_at}.'))

        # slugify title when published
        if self.published_at and not self.slug:
            self.slug = slugify(self.title)

        # it's tempting to validated published must be greater than created
        # but, there could be situations where backdating makes sense, like
        #   with data migration etc

    @property
    def meta_title_display(self):
        return self.meta_title or self.title

    @property
    def meta_description_display(self):
        return self.meta_description or self.description
