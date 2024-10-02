from http import HTTPStatus

from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        self.unauthorized_user = Client()

    def test_unexisting_page(self):
        response = self.unauthorized_user.get("/unexisting_page/")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
