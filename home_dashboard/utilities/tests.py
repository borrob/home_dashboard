"""
Testing of all the classes and endpoints for the utilities app.
"""
import datetime
from django.contrib.auth.models import User, Permission
from django.test import Client, TestCase
from django.urls import reverse

from .exceptions import MeterError, ReadingError
from .models import Meter, Reading
from .models import calculate_reading_on_date

# Create your tests here.

class MeterViewTests(TestCase):
    """
    Test the functionality of the Meter endpoint.

    Adds, deletes and edits the meters class and checks if the user has the
    right permissions.
    """

    # pylint: disable=invalid-name

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
        response = self.client.post(reverse('utilities:add_meter'),
                                    data={'meter_name': 'test',
                                          'unit_name': 'm'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please login")

    def test_add_meter_with_permission(self):
        """
        Test if someone with permission can add a meter (should be yes).
        """
        p = Permission.objects.get(name='Can add meter')
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.post(reverse('utilities:add_meter'),
                                    data={'meter_name': 'testmeter',
                                          'unit_name': 'm'},
                                    follow=True)
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
        response = self.client.post(reverse('utilities:add_meter'),
                                    data={'meter_name': 'testmeter',
                                          'unit_name': 'm'},
                                    follow=True)
        response = self.client.post(reverse('utilities:delete_meter'),
                                    data={'meter_name': 'testmeter'},
                                    follow=True)
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
        self.client.post(reverse('utilities:add_meter'),
                         data={'meter_name': 'testmeter',
                               'unit_name': 'm'},
                         follow=True)
        response = self.client.post(reverse('utilities:delete_meter'),
                                    data={'meter_name': 'testmeter'},
                                    follow=True)
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
        response = self.client.post(reverse('utilities:add_meter'),
                                    data={'meter_name': 'testmeter',
                                          'unit_name': 'm'},
                                    follow=True)
        response = self.client.post(reverse('utilities:edit_meter'),
                                    data={'meter_name': 'testmeter',
                                          'unit_name': 's',
                                          'new_name': 'thenewmeter'},
                                    follow=True)
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
        self.client.post(reverse('utilities:add_meter'),
                         data={'meter_name': 'testmeter',
                               'unit_name': 'm'},
                         follow=True)
        response = self.client.post(reverse('utilities:edit_meter'),
                                    data={'meter_name': 'testmeter',
                                          'unit_name': 's',
                                          'new_name': 'thenewmeter'},
                                    follow=True)
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
        self.client.post(reverse('utilities:add_meter'),
                         data={'meter_name': 'testmeter',
                               'unit_name': 'm'},
                         follow=True)
        self.client.post(reverse('utilities:add_meter'),
                         data={'meter_name': 'nametaken',
                               'unit_name': 'm'},
                         follow=True)
        response = self.client.post(reverse('utilities:edit_meter'),
                                    data={'meter_name': 'testmeter',
                                          'unit_name': 's',
                                          'new_name': 'nametaken'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testmeter")
        self.assertContains(response, "Name is already taken")

class ReadingViewTests(TestCase):
    """
    Test the functionality of the Reading endpoint.

    Adds, deletes and edits the readings class and checks if the user has the
    right permissions.
    """

    # pylint: disable=invalid-name

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
        m = Meter.objects.create(meter_name='testmeter', meter_unit='test')
        m.save()
        response = self.client.post(reverse('utilities:add_reading'),
                                    data={'date': '2018-04-04',
                                          'reading': 5,
                                          'meter': m.id,
                                          'remark': 'test'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please login")

    def test_add_reading_with_permission(self):
        """
        Test if someone with permission can add a reading (should be yes).
        """
        p = Permission.objects.get(name='Can add reading')
        self.user.user_permissions.add(p)
        self.client.login(username='testuser', password='q2w3E$R%')
        m = Meter.objects.create(meter_name='testmeter', meter_unit='test')
        m.save()
        response = self.client.post(reverse('utilities:add_reading'),
                                    data={'date': '2018-04-04',
                                          'reading': 5,
                                          'meter': m.id,
                                          'remark': 'test'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No reading yet")
        self.assertContains(response, '5')

    def test_remove_reading(self):
        """
        Test if anyone can delete a reading (no!)
        """
        m = Meter.objects.create(meter_name='testmeter', meter_unit='test')
        m.save()
        r = Reading.objects.create(date='2018-03-12', reading=99, meter=m)
        r.save()

        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.post(reverse('utilities:delete_reading'),
                                    data={'reading_id': r.id},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please login")

    def test_remove_reading_with_permission(self):
        """
        Test if anyone with permission can delete a reading (yes)
        """
        m = Meter.objects.create(meter_name='testmeter', meter_unit='test')
        m.save()
        r = Reading.objects.create(date='2018-03-12', reading=99, meter=m)
        r.save()
        p = Permission.objects.get(name='Can delete reading')
        self.user.user_permissions.add(p)

        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.post(reverse('utilities:delete_reading'),
                                    data={'reading_id': r.id},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No readings yet")
        self.assertContains(response, "is deleted")

    def test_change_reading(self):
        """
        Test if anyone can change a reading (should be no).
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        m = Meter.objects.create(meter_name='testmeter', meter_unit='test')
        m.save()
        r = Reading.objects.create(date='2018-03-12', reading=99, meter=m)
        r.save()

        response = self.client.post(reverse('utilities:edit_reading'),
                                    data={'date': '2018-04-04',
                                          'reading': 5,
                                          'meter': m.id,
                                          'remark': 'test'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please login")

    def test_change_reading_with_permission(self):
        """
        Test if someone with permission can change a reading (should be yes).
        """
        self.client.login(username='testuser', password='q2w3E$R%')
        m = Meter.objects.create(meter_name='testmeter', meter_unit='test')
        m.save()
        r = Reading.objects.create(date='2018-03-12', reading=99, meter=m)
        r.save()
        p = Permission.objects.get(name='Can delete reading')
        self.user.user_permissions.add(p)

        response = self.client.post(reverse('utilities:edit_reading'),
                                    data={'date': '2018-04-04',
                                          'reading': 5,
                                          'meter': m.id,
                                          'remark': 'test'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5")
        self.assertNotContains(response, "99")

class UsageTests(TestCase):
    """
    Test the usage.
    """

    def test_correct_usage_calculation(self):
        """
        Test to see if the useage is correctly calculated.
        """
        meter = Meter(meter_name='testmeter', meter_unit='m')
        reading_1 = Reading(date=datetime.date(2018, 1, 1),
                            reading=1,
                            meter=meter)
        reading_2 = Reading(date=datetime.date(2018, 1, 10),
                            reading=10,
                            meter=meter)
        my_date = datetime.date(2018, 1, 5)
        use = calculate_reading_on_date(my_date, reading_1, reading_2)
        self.assertEqual(use, 5)

    def test_error_usage_diff_meters(self):
        """
        Test the error message for calculating the usage on different meters.
        """

        meter_1 = Meter(meter_name='testmeter', meter_unit='m')
        meter_2 = Meter(meter_name='testmeter2', meter_unit='s')
        reading_1 = Reading(date=datetime.date(2018, 1, 1),
                            reading=1,
                            meter=meter_1)
        reading_2 = Reading(date=datetime.date(2018, 1, 10),
                            reading=10,
                            meter=meter_2)
        my_date = datetime.date(2018, 1, 5)
        try:
            calculate_reading_on_date(my_date, reading_1, reading_2)
        except MeterError:
            pass
        else:
            self.fail('Expected MeterError')

    def test_usage_on_same_date(self):
        """
        Test to see if the useage is correctly calculated.
        """
        meter = Meter(meter_name='testmeter', meter_unit='m')
        reading_1 = Reading(date=datetime.date(2018, 1, 1),
                            reading=1,
                            meter=meter)
        reading_2 = Reading(date=datetime.date(2018, 1, 1),
                            reading=10,
                            meter=meter)
        my_date = datetime.date(2018, 1, 5)
        try:
            calculate_reading_on_date(my_date, reading_1, reading_2)
        except ReadingError:
            pass
        else:
            self.fail('Expected ReadingError')
