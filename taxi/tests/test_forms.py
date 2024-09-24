from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.forms import (
    DriverCreationForm,
    CarForm,
    DriverLicenseUpdateForm,
)
from taxi.models import Manufacturer, Car


class FormTests(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name="testname",
            country="testcountry"
        )
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
        queryset = get_user_model().objects.filter(id=1)
        form_data = {
            "model": "testmodel",
            "drivers": queryset,
            "manufacturer": self.manufacturer
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
        expected_url_result = "username=e"
        expected_query_result = get_user_model().objects.filter(
            username__icontains="e"
        )
        data = {"username": "e"}
        response = self.client.get(reverse("taxi:driver-list"), data)
        url_result = response.request["QUERY_STRING"]
        query_result = response.context["object_list"]

        self.assertEqual(expected_url_result, url_result)
        self.assertEqual(list(expected_query_result), list(query_result))

    def test_car_search_form(self):
        Car.objects.create(
            model="testmodel",
            manufacturer=self.manufacturer
        )
        expected_url_result = "model=o"
        expected_query_result = Car.objects.filter(model__icontains="o")
        data = {"model": "o"}
        response = self.client.get(reverse("taxi:car-list"), data)
        url_result = response.request["QUERY_STRING"]
        query_result = response.context["object_list"]

        self.assertEqual(expected_url_result, url_result)
        self.assertEqual(list(expected_query_result), list(query_result))

    def test_manufacturer_search_form(self):
        expected_url_result = "name=a"
        expected_query_result = Manufacturer.objects.filter(
            name__icontains="a"
        )
        data = {"name": "a"}
        response = self.client.get(reverse("taxi:manufacturer-list"), data)
        url_result = response.request["QUERY_STRING"]
        query_result = response.context["object_list"]

        self.assertEqual(expected_url_result, url_result)
        self.assertEqual(list(expected_query_result), list(query_result))
