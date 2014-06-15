from __future__ import unicode_literals

from django.test import TestCase
from django.test.utils import override_settings, override_with_test_loader

from ..models import UrlArticle


@override_settings(ROOT_URLCONF='view_tests.urls')
class DefaultsTests(TestCase):
    """Test django views in django/views/defaults.py"""
    fixtures = ['testdata.json']
    non_existing_urls = ['/non_existing_url/',  # this is in urls.py
                         '/other_non_existing_url/']  # this NOT in urls.py

    def test_page_not_found(self):
        "A 404 status is returned by the page_not_found view"
        for url in self.non_existing_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

    def test_csrf_token_in_404(self):
        """
        The 404 page should have the csrf_token available in the context
        """
        # See ticket #14565
        for url in self.non_existing_urls:
            response = self.client.get(url)
            csrf_token = response.context['csrf_token']
            self.assertNotEqual(str(csrf_token), 'NOTPROVIDED')
            self.assertNotEqual(str(csrf_token), '')

    def test_server_error(self):
        "The server_error view raises a 500 status"
        response = self.client.get('/server_error/')
        self.assertEqual(response.status_code, 500)

    def test_custom_templates(self):
        """
        Test that 404.html and 500.html templates are picked by their respective
        handler.
        """
        with override_with_test_loader({
                '404.html': 'This is a test template for a 404 error.',
                '500.html': 'This is a test template for a 500 error.'}):
            for code, url in ((404, '/non_existing_url/'), (500, '/server_error/')):
                response = self.client.get(url)
                self.assertContains(response, "test template for a %d error" % code,
                    status_code=code)

    def test_get_absolute_url_attributes(self):
        "A model can set attributes on the get_absolute_url method"
        self.assertTrue(getattr(UrlArticle.get_absolute_url, 'purge', False),
                        'The attributes of the original get_absolute_url must be added.')
        article = UrlArticle.objects.get(pk=1)
        self.assertTrue(getattr(article.get_absolute_url, 'purge', False),
                        'The attributes of the original get_absolute_url must be added.')

    @override_settings(DEFAULT_CONTENT_TYPE="text/xml")
    def test_default_content_type_is_text_html(self):
        """
        Content-Type of the default error responses is text/html. Refs #20822.
        """
        response = self.client.get('/raises400/')
        self.assertEqual(response['Content-Type'], 'text/html')

        response = self.client.get('/raises403/')
        self.assertEqual(response['Content-Type'], 'text/html')

        response = self.client.get('/non_existing_url/')
        self.assertEqual(response['Content-Type'], 'text/html')

        response = self.client.get('/server_error/')
        self.assertEqual(response['Content-Type'], 'text/html')

    def test_4xx(self):
        response1 = self.client.get('/raises4xx/405/')
        response2 = self.client.get('/raises4xx/404/')
        self.assertEqual(response1.status_code, 405)
        self.assertEqual(response2.status_code, 404)
        self.assertContains(response1, '<h1>METHOD NOT ALLOWED (405)</h1>', status_code=405)
        self.assertContains(response2, '<h1>NOT FOUND (404)</h1>', status_code=404)

    def test_4xx_template(self):
        # Set up a test 403.html template.
        with override_with_test_loader({'405.html': 'This is a test template '
                                        'for 405.'}):
            response = self.client.get('/raises4xx/405/')
            self.assertContains(response, 'test template for 405', status_code=405)

    def test_5xx(self):
        response1 = self.client.get('/raises5xx/500/')
        response2 = self.client.get('/raises5xx/507/')
        self.assertEqual(response1.status_code, 500)
        self.assertEqual(response2.status_code, 507)
        self.assertContains(response1, '<h1>INTERNAL SERVER ERROR (500)</h1>', status_code=500)
        self.assertContains(response2, '<h1>INSUFFICIENT STORAGE (507)</h1>', status_code=507)

    def test_5xx_template(self):
        # Set up a test 403.html template.
        with override_with_test_loader({'500.html': 'This is a test template '
                                        'for 500.'}):
            response = self.client.get('/raises5xx/500/')
            self.assertContains(response, 'test template for 500', status_code=500)
