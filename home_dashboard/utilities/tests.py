from django.contrib.auth.models import User, Permission
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
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No meters yet")

    def test_add_meter(self):
        """
        Test if anyone can add a meter (should be no).
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'test', 'unit_name': 'm'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please login")

    def test_add_meter_with_permission(self):
        """
        Test if someone with permission can add a meter (should be yes).
        """
        p = Permission.objects.get(name='Can add meter')
        self.user.user_permissions.add(p.id)
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'testmeter', 'unit_name': 'm'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No meters yet")
        self.assertContains(response, 'testmeter')
