from http import HTTPStatus

from django.contrib.auth import get_user

from notes.tests.common import FixturesForTests


class TestRoutes(FixturesForTests):

    def test_pages_availability(self):
        urls = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)  # 200

    def test_availability_list_success_add(self):
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)  # 200

    def test_availability_detail_edit_delete_for_author(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),  # 200
            (self.not_author_client, HTTPStatus.NOT_FOUND),  # 404
        )
        for user, status in users_statuses:
            for url in (self.detail_url,
                        self.edit_url,
                        self.delete_url,
                        ):
                with self.subTest(user=get_user(user), url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_login(self):
        for urls in (
            self.list_url,
            self.success_url,
            self.add_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        ):
            with self.subTest(url=urls):
                redirect_url = f'{self.login_url}?next={urls}'
                response = self.client.get(urls)
                self.assertRedirects(response, redirect_url)
