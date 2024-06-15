from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст'
        )
        cls.reader = User.objects.create(
            username='Пользователь'
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse(
            'notes:edit',
            args=(cls.note.slug,)
        )

    def test_list_of_notes_user(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_list_author_ignore_reader(self):
        url = reverse('notes:list')
        response = self.reader_client.get(url)
        notes = response.context['object_list']
        self.assertNotIn(self.note, notes)

    def test_create_and_add_form(self):
        urls = (
            (self.add_url),
            (self.edit_url)
        )
        for url in urls:
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
