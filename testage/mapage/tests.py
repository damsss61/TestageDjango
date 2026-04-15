from django.test import TestCase

# Create your tests here.
from django.test import SimpleTestCase
from django.urls import reverse

class TestAccueil(SimpleTestCase):
    def test_accueil_status_code(self):
        response = self.client.get(reverse('accueil'))
        self.assertEqual(response.status_code, 200)