"""
Testing the API V1 REST interface.
"""
import json
from django.contrib.auth.models import User, Permission
from django.test import Client, TestCase
from django.urls import reverse

from utilities.models import Meter

class RestMeterTests(TestCase):
    """
    Test the REST functionality for the Meters.
    """
    # pylint: disable=invalid-name

    def setUp(self):
        """
        Setup a test user for login.
        """
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@user.com', 'q2w3E$R%')

    def test_need_login_to_see_meterlist(self):
        """
        The rest-interface should *not* be accessible for everyone.
        """
        response = self.client.get(reverse('api_v1:meter_list'), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_loging_can_see_meterlist(self):
        """
        Test authenticated users can see meterlist.
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        meter = Meter.objects.create(meter_name='testmeter', meter_unit='X')
        meter.save()
        response = self.client.get(reverse('api_v1:meter_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testmeter')
        self.assertContains(response, 'X')

    def test_need_login_to_post_new_meter(self):
        """
        The rest interface should *not* allow anyone to add new data.
        """
        data = {'meter_name': 'test', 'meter_unit': 'X'}
        response = self.client.post(reverse('api_v1:meter_list'), data=data, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_login_to_post_new_meter(self):
        """
        The rest interface should *not* allow anyone with a login to add new data.
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        data = {'meter_name': 'test', 'meter_unit': 'X'}
        response = self.client.post(reverse('api_v1:meter_list'), data=data, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_special_login_to_post_new_meter(self):
        """
        The rest interface should allow people with permission to add new data.
        """
        p = Permission.objects.get(name='Can add meter')
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        data = json.dumps({'meter_name': 'testmeter', 'meter_unit': 'X'})
        response = self.client.post(reverse('api_v1:meter_list'),
                                    data,
                                    follow=True,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('testmeter', str(response.content))
        self.assertIn('X', str(response.content))

    def test_no_two_meters_with_same_name(self):
        """
        The rest interface should allow people with permission to add new data.
        """
        p = Permission.objects.get(name='Can add meter')
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        data = json.dumps({'meter_name': 'test', 'meter_unit': 'X'})
        response1 = self.client.post(reverse('api_v1:meter_list'),
                                     data,
                                     follow=True,
                                     content_type='application/json')
        response2 = self.client.post(reverse('api_v1:meter_list'),
                                     data,
                                     follow=True,
                                     content_type='application/json')
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 400)

    def test_need_login_to_see_meterdetails(self):
        """
        The rest-interface should *not* be accessible for everyone.
        """
        url = reverse('api_v1:meter_details', args=[1])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_login_to_see_meterdetails(self):
        """
        The rest interface should allow any login to see the meterdetails.
        """
        meter = Meter.objects.create(meter_name='testmeter', meter_unit='X')
        meter.save()
        self.client.login(username='testuser', password='q2w3E$R%')
        url = reverse('api_v1:meter_details', args=[1])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testmeter')
        self.assertContains(response, 'X')

    def test_special_login_to_put_changes_to_meter(self):
        """
        The rest interface should allow people with permission to alter meter.
        """
        meter = Meter.objects.create(meter_name='testmeter', meter_unit='X')
        meter.save()

        p = Permission.objects.get(name='Can change meter')
        self.user.user_permissions.add(p)

        url = reverse('api_v1:meter_details', args=[1])
        self.client.login(username='testuser', password='q2w3E$R%')
        data = json.dumps({'meter_name': 'testmeter_altered'})
        response = self.client.put(url,
                                   data,
                                   follow=True,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('testmeter_altered', str(response.content))
        self.assertIn('X', str(response.content))

        data = json.dumps({'meter_unit': 'Y'})
        response = self.client.put(url,
                                   data,
                                   follow=True,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('testmeter_altered', str(response.content))
        self.assertIn('Y', str(response.content))

    def test_cannot_change_metername_to_existing_(self):
        """
        Changing a name of a meter to a name already in the database should not be ok.
        """
        meter = Meter.objects.create(meter_name='testmeter', meter_unit='X')
        meter.save()
        meter2 = Meter.objects.create(meter_name='testmeter_alt', meter_unit='X')
        meter2.save()

        p = Permission.objects.get(name='Can change meter')
        self.user.user_permissions.add(p)

        url = reverse('api_v1:meter_details', args=[2])
        self.client.login(username='testuser', password='q2w3E$R%')
        data = json.dumps({'meter_name': 'testmeter'})
        response = self.client.put(url,
                                   data,
                                   follow=True,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)
