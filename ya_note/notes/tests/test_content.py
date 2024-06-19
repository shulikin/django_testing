from notes.tests.common import FixturesForTests
from notes.forms import NoteForm


class TestContent(FixturesForTests):

    def test_list_of_notes_user(self):
        response = self.author_client.get(self.list_url)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

    def test_list_author_ignore_reader(self):
        response = self.not_author_client.get(self.list_url)
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
