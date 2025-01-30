import datetime
import uuid
from uuid import UUID
from copy import deepcopy

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker

from core.tests.factories import UserFactory
from core.models import Post
from core.models.blog import cover_image_file_path


fake = Faker()

class TestPost(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.required_for_publish = {
            'description': fake.paragraph(nb_sentences=2),
            'body': fake.paragraphs(nb=5),
            'cover_image': fake.file_name('image', 'jpg'),
            'cover_image_alt': fake.sentence(nb_words=5)
        }

    def setUp(self):
        post = Post.objects.create(
            title=fake.sentence(nb_words=7)[:60]
        )
        author = UserFactory()
        post.authors.add(author)
        self.author = author
        self.blog_post = post

    def test_post_str_method(self):
        self.assertEqual(
            str(self.blog_post),
            self.blog_post.title
        )

    def test_author_on_post(self):
        self.assertTrue(
            self.author in self.blog_post.authors.all()
        )

    def test_field_missing_for_publish(self):
        # use missing description
        # set all other fields required to publish
        missing_field = 'description'
        incomplete_fields = deepcopy(self.required_for_publish)
        incomplete_fields.pop(missing_field)

        for k, v in incomplete_fields.items():
            setattr(self.blog_post, k, v)

        with self.assertRaisesMessage(
            ValidationError,
            f'{missing_field.replace("_", " ").title()} is required to publish.'
        ) as cm:
            # set published
            self.blog_post.published_at = timezone.now()
            self.blog_post.save()

    def test_updated_before_published(self):
        for k, v in self.required_for_publish.items():
            setattr(self.blog_post, k, v)
        published = timezone.now()
        # set updated a day before
        updated = published - datetime.timedelta(days=1)
        self.blog_post.published_at = published
        self.blog_post.updated_at = updated

        with self.assertRaisesMessage(
            ValidationError,
            f'Update {updated} cannot occur before publish {published}.'
        ):
            self.blog_post.save()

    def test_title_sugified_on_publish(self):
        slug = slugify(self.blog_post.title)

        for k, v in self.required_for_publish.items():
            setattr(self.blog_post, k, v)

        self.blog_post.published_at = timezone.now()

        # remember, django stores char / text as an empty string
        self.assertEqual(
            getattr(self.blog_post, 'slug'),
            ''
        )
        self.blog_post.save()

        self.assertEqual(
            self.blog_post.slug,
            slug
        )

    def test_meta_display_methods(self):
        title = fake.sentence(nb_words=4)[:60]
        meta_title = fake.sentence(nb_words=5)[:60]
        description = fake.paragraph(nb_sentences=2)[:160]
        meta_description = fake.paragraph(nb_sentences=3)[:160]

        setattr(self.blog_post, 'title', title)
        setattr(self.blog_post, 'description', description)
        self.blog_post.save()

        self.assertEqual(self.blog_post.title, title)
        self.assertEqual(self.blog_post.description, description)
        self.assertEqual(self.blog_post.meta_title_display, title)
        self.assertEqual(self.blog_post.meta_description_display, description)

        setattr(self.blog_post, 'meta_title', meta_title)
        setattr(self.blog_post, 'meta_description', meta_description)
        self.blog_post.save()

        self.assertEqual(self.blog_post.meta_title, meta_title)
        self.assertEqual(self.blog_post.meta_description, meta_description)
        self.assertEqual(self.blog_post.meta_title_display, meta_title)
        self.assertEqual(self.blog_post.meta_description_display, meta_description)

    def test_cover_image_file_path_function(self):
        required_items = deepcopy(self.required_for_publish)
        file_name = required_items.pop('cover_image')
        for k, v in required_items.items():
            setattr(self.blog_post, k, v)

        self.blog_post.cover_image = SimpleUploadedFile(
            file_name,
            b'fake image bytes.'
        )

        self.assertEqual(
            file_name,
            self.blog_post.cover_image
        )
        self.blog_post.save()

        def _is_valid_uuid(value: str) -> bool:
            # make sure to match uuid verion in tested function
            # make sure a string is pased otherwise you'll get a TypeError
            #   raised and not a ValueError as expected
            try:
                uuid_obj = uuid.UUID(value, version=4)
                return str(uuid_obj) == value
            except ValueError:
                return False

        # to verify method works
        self.assertFalse(_is_valid_uuid('not-uuid'))

        # split off path prefix
        path_prefix ,processed_file_name = self.blog_post.cover_image.name.split('/')

        # lose the extension
        no_ext = processed_file_name.split('.')[0]

        # test for uuid formatting
        self.assertTrue(_is_valid_uuid(no_ext))

        # test path prefix
        self.assertEqual(
            path_prefix,
            'post-cover-images'
        )
