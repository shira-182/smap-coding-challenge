from datetime import date, datetime

from django.test import TestCase
from django.urls import reverse

from consumption.models import CalculatedConsumption, Consumption, User


class SummaryViewTests(TestCase):
    def setUp(self):
        user = User.objects.create(id=3000, area="a1", tariff="t1")
        user2 = User.objects.create(id=3001, area="a2", tariff="t2")

        Consumption.objects.create(
            user=user, datetime=datetime(2016, 11, 1, 0, 00, 0), consumption=10.0
        )
        Consumption.objects.create(
            user=user, datetime=datetime(2016, 12, 1, 0, 00, 0), consumption=11.0
        )
        Consumption.objects.create(
            user=user, datetime=datetime(2016, 12, 1, 0, 30, 0), consumption=12.0
        )

        CalculatedConsumption.objects.create(date=date(2016, 11, 1), sum=10.0)
        CalculatedConsumption.objects.create(date=date(2016, 12, 1), sum=23.0)

    def test_get(self):
        res = self.client.get(reverse("summary"))
        self.assertEqual(res.status_code, 200, msg="リクエストが成功すること")
        self.assertEqual(res.context["object_list"].model, User)
        self.assertEqual(res.context["object_list"].count(), User.objects.count())

    def test_get_no_user(self):
        User.objects.all().delete()
        Consumption.objects.all().delete()
        CalculatedConsumption.objects.all().delete()

        res = self.client.get(reverse("summary"))
        self.assertEqual(res.status_code, 200, msg="リクエストが成功すること")


class DetailViewTests(TestCase):
    def setUp(self):
        user = User.objects.create(id=3000, area="a1", tariff="t1")

        Consumption.objects.create(
            user=user, datetime=datetime(2016, 11, 1, 0, 00, 0), consumption=10.0
        )
        Consumption.objects.create(
            user=user, datetime=datetime(2016, 12, 1, 0, 00, 0), consumption=11.0
        )
        Consumption.objects.create(
            user=user, datetime=datetime(2016, 12, 1, 0, 30, 0), consumption=12.0
        )

    def test_get(self):
        res = self.client.get(reverse("detail", args=[3000]))
        self.assertEqual(res.status_code, 200, msg="リクエストが成功すること")
        self.assertEqual(res._headers["content-type"][1], "image/svg+xml")

    def test_get_not_exists_err(self):
        res = self.client.get(reverse("detail", args=[4000]))
        self.assertEqual(res.status_code, 404, msg="存在しないuser.pkを指定すると、リクエストが失敗すること")
