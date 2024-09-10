from re import search

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.forms import DriverCreationForm, CarForm, DriverLicenseUpdateForm, DriverSearchForm
from taxi.models import Manufacturer, Driver


class FormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test",
            password="password123"
        )
        self.client.force_login(self.user)

    def test_driver_creation_with_valid_license_number_first_last_name(self):
        form_data = {
            "username": "new_user",
            "first_name": "firstuser",
            "last_name": "lastuser",
            "password1": "user123test",
            "password2": "user123test",
            "license_number": "QAZ12345",
        }
        form = DriverCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

        self.client.post(reverse("taxi:driver-create"), data=form_data)
        new_user = get_user_model().objects.get(username=form_data["username"])
        self.assertEqual(new_user.license_number, form_data["license_number"])

    def test_car_creation(self):
        manufacturer = Manufacturer.objects.create(
            name="testname",
            country="testcountry"
        )
        queryset = get_user_model().objects.filter(id=1)
        form_data = {
            "model": "testmodel",
            "drivers":  queryset,
            "manufacturer": manufacturer
        }
        form = CarForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["model"], form_data["model"])
        self.assertEqual(form.cleaned_data["manufacturer"], form_data["manufacturer"])
        self.assertEqual(list(form.cleaned_data["drivers"]), list(form_data["drivers"]))
# --------------------------------------------------------
    def test_license_update_validation_form(self):
        data = {"license_number": "AAA00000"}
        data_f = {"license_number": "AA0000"}
        res = reverse("taxi:driver-update", args=[self.user.id])
        self.user.license_number="QAZ12345"
        self.user.save()
        form = DriverLicenseUpdateForm(data=data)
        self.assertTrue(form.is_valid())
        form = DriverLicenseUpdateForm(data=data_f)
        self.assertFalse(form.is_valid())

        patched_user = self.client.put(res, data=data, content_type="application/json")

        print(patched_user)
        self.assertEqual(patched_user.status_code, 200)
        self.assertEqual(patched_user.content, 'request method: PUT')
        self.assertEqual(self.user.license_number, data)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def test_driver_search_form(self):
        search_form = DriverSearchForm(data={"username": "a"})
        response = self.client.get(reverse("taxi:driver-list"), {"username": "a"})

        print(response.request)
