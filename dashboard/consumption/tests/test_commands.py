# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from consumption.models import CalculatedConsumption, Consumption, User


class ImportTest(TestCase):
    def test_import(self):
        out = StringIO()
        err = StringIO()
        call_command(
            "import",
            "../data/user_data.csv",
            "../data/consumption/",
            stdout=out,
            stderr=err,
        )

        self.assertEqual(User.objects.all().count(), 60)
        self.assertEqual(Consumption.objects.all().count(), 489600)
        self.assertEqual(CalculatedConsumption.objects.count(), 170)
