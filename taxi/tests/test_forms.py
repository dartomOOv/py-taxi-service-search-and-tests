from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.forms import (
    DriverCreationForm,
    CarForm,
    DriverLicenseUpdateForm,
)
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
            "drivers": queryset,
            "manufacturer": manufacturer
        }
        form = CarForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["model"], form_data["model"])
        self.assertEqual(
            form.cleaned_data["manufacturer"],
            form_data["manufacturer"]
        )
        self.assertEqual(
            list(form.cleaned_data["drivers"]),
            list(form_data["drivers"])
        )

    def test_license_update_form(self):
        old_license = "QAZ12345"
        new_license = "AAA00000"
        data = {"license_number": new_license}
        self.user.license_number = old_license
        self.user.save()
        form = DriverLicenseUpdateForm(instance=self.user, data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(self.user.license_number, new_license)

    def test_driver_search_form(self):
        expected_result = "username=a"
        data = {"username": "a"}
        response = self.client.get(reverse("taxi:driver-list"), data)
        self.assertEqual(expected_result, response.request["QUERY_STRING"])

    def test_car_search_form(self):
        expected_result = "model=a"
        data = {"model": "a"}
        response = self.client.get(reverse("taxi:car-list"), data)
        self.assertEqual(expected_result, response.request["QUERY_STRING"])

    def test_manufacturer_search_form(self):
        expected_result = "name=a"
        data = {"name": "a"}
        response = self.client.get(reverse("taxi:manufacturer-list"), data)
        self.assertEqual(expected_result, response.request["QUERY_STRING"])
