"""
Testing of all the classes and endpoints for the utilities app.
"""
import datetime
from django.contrib.auth.models import User, Permission
from django.db import IntegrityError
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from .exceptions import MeterError
from .models import Meter, Reading, Usage
from .models import calculate_reading_on_date
from .models import update_usage_after_new_reading

# Create your tests here.

class MeterViewTests(TransactionTestCase):
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

    def test_add_meter_with_same_name(self):
        """
        Test cannot add second meter with same name.
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
        response = self.client.post(reverse('utilities:add_meter'),
                                    data={'meter_name': 'testmeter',
                                          'unit_name': 'm'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Meter already exists.')

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

    def test_remove_non_existing_meter(self):
        """
        Test expected error on deleting a meter that doesn't exist.
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
                                    data={'meter_name': 'NONEXISTING'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testmeter")
        self.assertNotContains(response, "testmeter is deleted")
        self.assertNotContains(response, "NONEXISTING")

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

    def test_cannot_store_two_readings_on_same_data_with_same_meter(self):

        """
        Test to see if the useage is correctly calculated.
        """
        meter = Meter(meter_name='testmeter', meter_unit='m')
        meter.save()
        reading_1 = Reading(date=datetime.date(2018, 1, 1),
                            reading=1,
                            meter=meter)
        reading_2 = Reading(date=datetime.date(2018, 1, 1),
                            reading=10,
                            meter=meter)
        try:
            reading_1.save()
            reading_2.save()
        except IntegrityError:
            pass
        else:
            self.fail('Expected unique constraint error.')


class UsageTests(TestCase):
    """
    Test the usage.
    """
    def setUp(self):
        """
        Setup a test user for login.
        """
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@user.com', 'q2w3E$R%')

    def test_correct_usage_calculation(self):
        """
        Test to see if the useage is correctly calculated.
        Readings (at beginning of each day):
            2018-01-01: 0
            2018-01-02: 1
            2018-01-03: 2
            2018-01-04: 3
            2018-01-05: 4
            2018-01-06: 5
            2018-01-07: 6
            2018-01-08: 7
            2018-01-09: 8
            2018-01-10: 9
            2018-01-11: 10
        """
        meter = Meter(meter_name='testmeter', meter_unit='m')
        reading_1 = Reading(date=datetime.date(2018, 1, 1),
                            reading=0,
                            meter=meter)
        reading_2 = Reading(date=datetime.date(2018, 1, 11),
                            reading=10,
                            meter=meter)
        my_date = datetime.date(2018, 1, 6)
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
        reading = calculate_reading_on_date(my_date, reading_1, reading_2)
        self.assertEqual(reading_1.reading, reading)

    def test_usage_calc_on_insert(self):
        """
        Test if the usage is calculated correctly on inserting a new reading.
        """
        meter = Meter(meter_name='testmeter', meter_unit='m')
        meter.save()
        reading_1 = Reading(date=datetime.date(2018, 7, 1),
                            reading=0,
                            meter=meter)
        reading_2 = Reading(date=datetime.date(2018, 9, 1),
                            reading=10,
                            meter=meter)
        reading_1.save()
        reading_2.save()
        update_usage_after_new_reading(reading_2)
        use = Usage.objects.get(month=8, year=2018, meter=meter.id)
        self.assertEqual(use.usage, 5)

        self.client.login(username='testuser', password='q2w3E$R%')
        response = self.client.get(reverse('utilities:usage_list'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5")
