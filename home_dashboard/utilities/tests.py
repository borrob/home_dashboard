from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

# Create your tests here.

class MeterViewTests(TestCase):

    def setUp(self):
        """
        Setup a test user for login.
        """
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@user.com', 'q2w3E$R%')

    def test_need_login_for_meterlist(self):
        """
        Trying to see the list withou login should redirect to login page.
        """
        response = self.client.get(reverse('utilities:meter_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")

    def test_no_meters(self):
        """
        Test the response if there are no meters present
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.get(reverse('utilities:meter_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No meters yet")
