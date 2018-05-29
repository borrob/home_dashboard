"""
Testing the API V1 REST interface.
"""
import json
from datetime import datetime
from django.contrib.auth.models import User, Permission
from django.test import Client, TestCase
from django.urls import reverse

from utilities.models import Meter, Reading

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


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

    def test_login_can_see_meterlist(self):
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


class RestReadingTests(TestCase):
    """
    Provides test cases for the Readings rest interface.
    """

    # pylint: disable=invalid-name

    def setUp(self):
        """
        Setup a test user for login.
        """
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@user.com', 'q2w3E$R%')
        meter = Meter.objects.create(meter_name='testmeter', meter_unit='X')
        meter.save()
        reading = Reading.objects.create(meter=meter,
                                         reading=100,
                                         date=datetime.strptime('2001-01-01', '%Y-%m-%d').date(),
                                         remark='test reading')
        reading.save()

    def test_need_login_to_see_readinglist(self):
        """
        The rest-interface should *not* be accessible for everyone.
        """
        response = self.client.get(reverse('api_v1:reading_list'), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_login_can_see_readinglist(self):
        """
        Readinglist is available to logged in members.
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.get(reverse('api_v1:reading_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test reading')
        self.assertContains(response, '2001')
        self.assertContains(response, '100')

    def test_login_cannot_add_new_reading(self):
        """
        Not everyone can add a meter.
        Trying to post data as XML
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        data = XML_HEADER + '<root>' + \
            '  <date>2018-01-10</date>' + \
            '  <reading>-200.00</reading>' + \
            '  <meter>1</meter>' + \
            '  <remark>testnew</remark>' + \
            '</root>'
        response = self.client.post(reverse('api_v1:reading_list'),
                                    data=data,
                                    content_type='application/xml',
                                    follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('testnew', str(response.content))

    def test_special_login_can_add_reading(self):
        """
        Adding a meter require login.
        Trying to post data as XML.
        """
        p = Permission.objects.get(name='Can add reading')
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        data = XML_HEADER + '<root>' + \
            '  <date>2018-01-10</date>' + \
            '  <reading>-200.00</reading>' + \
            '  <meter>1</meter>' + \
            '  <remark>testnew</remark>' + \
            '</root>'
        response = self.client.post(reverse('api_v1:reading_list'),
                                    data=data,
                                    content_type='application/xml',
                                    follow=True)
        self.assertEqual(response.status_code, 201)
        self.assertIn('testnew', str(response.content))

    def test_need_login_to_see_reading_details(self):
        """
        Login is required to see the reading details
        """
        response = self.client.get(reverse('api_v1:reading_details', args=[1]), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_login_can_see_reading_details(self):
        """
        With login reading details are available.
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.get(reverse('api_v1:reading_details', args=[1]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test reading')
        self.assertContains(response, '2001')
        self.assertContains(response, '100')

    def test_need_login_to_change_reading_details(self):
        """
        Not anyone can change reading details.
        """
        data = {'reading': 500}
        response = self.client.put(reverse('api_v1:reading_details', args=[1]),
                                   content_type='application/json',
                                   follow=True,
                                   data=json.dumps(data))
        self.assertEqual(response.status_code, 403)

    def test_not_every_loging_can_change_reading_details(self):
        """
        Special permission is required.
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        data = {'reading': 500}
        response = self.client.put(reverse('api_v1:reading_details', args=[1]),
                                   content_type='application/json',
                                   follow=True,
                                   data=json.dumps(data))
        self.assertEqual(response.status_code, 403)

    def test_login_can_change_reading(self):
        """
        Login with permission can change reading.
        """
        p = Permission.objects.get(name='Can change reading')
        self.user.user_permissions.add(p)
        self.user.save()
        self.client.login(username='testuser', password='q2w3E$R%')
        data = {'reading': 500}
        response = self.client.put(reverse('api_v1:reading_details', args=[1]),
                                   content_type='application/json',
                                   follow=True,
                                   data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 500)
        self.assertContains(response, 2001)
