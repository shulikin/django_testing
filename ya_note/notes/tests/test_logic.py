from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

URL_SUCCESS = reverse('notes:success')
URL_ADD = reverse('notes:add')
TEXT = 'Текст'
TITLE = 'Заголовок'
SLUG = 'slug'


class TestNoteCreation(TestCase):


    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='Пользователь'
        )
        cls.notes_counts = Note.objects.count()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': TEXT,
            'title': TITLE,
            'slug': SLUG,
            'author': cls.auth_client
            }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(URL_ADD, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(URL_ADD, data=self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.notes_counts + 1)
        note = Note.objects.get()
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.text, TEXT)
        self.assertEqual(note.slug, SLUG)
        self.assertEqual(note.author, self.user)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_client.post(URL_ADD, data=self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        self.assertEqual(Note.objects.count(), self.notes_counts + 1)


class TestNoteEditDelete(TestCase):
    NEW_TEXT = 'Новый текст'
    NEW_TITLE = 'Новый заголовок'
    NEW_SLUG = 'new_slug'

    @classmethod
    def setUpTestData(cls):
        cls.notes_counts = Note.objects.count()
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            author=cls.author,
            text=TEXT,
            title=TITLE,
            slug=SLUG
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'text': cls.NEW_TEXT,
                         'title': cls.NEW_TITLE,
                         'slug': cls.NEW_SLUG}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, URL_SUCCESS)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_counts)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)  # 404Err
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_counts + 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)  # 404Err
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TEXT)

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            URL_ADD,
            data=self.form_data
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(
            Note.objects.count(),
            self.notes_counts + 1
        )
