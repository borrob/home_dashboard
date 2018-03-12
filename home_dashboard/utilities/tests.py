from django.contrib.auth.models import User, Permission
from django.test import Client, TestCase
from django.urls import reverse

from .models import Meter

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
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'testmeter', 'unit_name': 'm'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No meters yet")
        self.assertContains(response, 'testmeter')

    def test_remove_meter(self):
        """
        Test if anyone can delete a meter (no!)
        """
        p = Permission.objects.get(name='Can add meter')
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'testmeter', 'unit_name': 'm'}, follow=True)
        response = self.client.post(reverse('utilities:delete_meter'), data={'meter_name': 'testmeter'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please login")

    def test_remove_meter_with_permission(self):
        """
        Test if someone with permission can delete a meter (yes)
        """
        p = Permission.objects.get(name='Can add meter')
        p2 = Permission.objects.get(name='Can delete meter')
        self.user.user_permissions.add(p)
        self.user.user_permissions.add(p2)
        self.client.login(username='testuser', password='q2w3E$R%')
        self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'testmeter', 'unit_name': 'm'}, follow=True)
        response = self.client.post(reverse('utilities:delete_meter'), data={'meter_name': 'testmeter'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No meters yet")
        self.assertContains(response, "testmeter is deleted")

    def test_change_meter(self):
        """
        Test if anyone can change a mter (No!)
        """
        p = Permission.objects.get(name='Can add meter')
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'testmeter', 'unit_name': 'm'}, follow=True)
        response = self.client.post(reverse('utilities:edit_meter'), data={'meter_name': 'testmeter', 'unit_name': 's', 'new_name': 'thenewmeter'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please login")

    def test_edit_meter_with_permission(self):
        """
        Test if someone with permission can change a meter (yes)
        """
        p = Permission.objects.get(name='Can add meter')
        p2 = Permission.objects.get(name='Can change meter')
        self.user.user_permissions.add(p)
        self.user.user_permissions.add(p2)
        self.client.login(username='testuser', password='q2w3E$R%')
        self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'testmeter', 'unit_name': 'm'}, follow=True)
        response = self.client.post(reverse('utilities:edit_meter'), data={'meter_name': 'testmeter', 'unit_name': 's', 'new_name': 'thenewmeter'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "thenewmeter")
        self.assertContains(response, "thenewmeter is changed")

    def test_edit_meter_with_permission_to_name_already_taken(self):
        """
        Test if someone with permission can change a meter (yes)
        """
        p = Permission.objects.get(name='Can add meter')
        p2 = Permission.objects.get(name='Can change meter')
        self.user.user_permissions.add(p)
        self.user.user_permissions.add(p2)
        self.client.login(username='testuser', password='q2w3E$R%')
        self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'testmeter', 'unit_name': 'm'}, follow=True)
        self.client.post(reverse('utilities:add_meter'), data={'meter_name': 'nametaken', 'unit_name': 'm'}, follow=True)
        response = self.client.post(reverse('utilities:edit_meter'), data={'meter_name': 'testmeter', 'unit_name': 's', 'new_name': 'nametaken'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testmeter")
        self.assertContains(response, "Name is already taken")

class ReadingViewTests(TestCase):

    def setUp(self):
        """
        Setup a test user for login.
        """
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@user.com', 'q2w3E$R%')

    def test_need_login_for_readinglist(self):
        """
        Trying to see the list without login should redirect to login page.
        """
        response = self.client.get(reverse('utilities:reading_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")

    def test_no_readings(self):
        """
        Test the response if there are no readings present
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.get(reverse('utilities:reading_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No readings yet")

    def test_add_reading(self):
        """
        Test if anyone can add a reading (should be no).
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        m = Meter.objects.create(meter_name='testmeter', unit_name='test')
        m.save()
        resonse = self.client.post(reverse('utilities:add_reading'), data={'date': '2018-04-04', 'reading': 5, 'meter': m.id, 'remark': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please login")

    def test_add_reading_with_permission(self):
        """
        Test if someone with permission can add a reading (should be yes).
        """
        p = Permission.objects.get(name='Can add reading')
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        m = Meter.objects.create(meter_name='testmeter', unit_name='test')
        m.save()
        resonse = self.client.post(reverse('utilities:add_reading'), data={'date': '2018-04-04', 'reading': 5, 'meter': m.id, 'remark': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No reading yet")
        self.assertContains(response, '5')

