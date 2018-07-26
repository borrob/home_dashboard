"""
Testing of the general dashboard app.
"""
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class DashboardTest(TestCase):
    """
    Test the dashboard.
    """

    # pylint: disable=invalid-name

    def setUp(self):
        """
        Setup a test user for login.
        """
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@user.com', 'q2w3E$R%')

    def test_version(self):
        """
        Test if the version number is shown.
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.get(reverse('dashboard:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Version")
