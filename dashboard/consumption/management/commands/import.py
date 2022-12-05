import time

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.db.models.functions import TruncDay

from consumption.mixins import LoggingMixin
from consumption.models import CalculatedConsumption, Consumption, User


class Command(BaseCommand, LoggingMixin):
    help = "import data"

    def add_arguments(self, parser):
        parser.add_argument("user_file_path", type=str, help="ex)../data/user_data.csv")
        parser.add_argument(
            "consumption_dir_path", type=str, help="ex)../data/consumption/"
        )

    def handle(self, *args, **options):
        start_time = time.perf_counter()

        self._upsert_user(options["user_file_path"])
        self._upsert_consumption(options["consumption_dir_path"])
        self._upsert_total_consumption()

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        data = {
            "処理にかかった時間": elapsed_time,
            "userのレコード数": User.objects.all().count(),
            "consumptionのレコード数": Consumption.objects.all().count(),
            "total_consumptionのレコード数": CalculatedConsumption.objects.all().count(),
        }
        self.logger.info("%s", data)

    def _upsert_user(self, user_file_path: str) -> None:
        df_csv = pd.read_csv(user_file_path, encoding="utf-8")
        if len(df_csv) == User.objects.all().count():
            return

        User.objects.bulk_create(User(**row) for row in df_csv.to_dict("records"))

    def _upsert_consumption(self, consumption_dir_path: str) -> None:
        users_id_list = User.objects.all().values_list("id", flat=True)
        for user_id in users_id_list:
            file_name = f"{consumption_dir_path}{user_id}.csv"
            df_csv = pd.read_csv(file_name, encoding="utf-8")
            df_not_duplicate = df_csv.drop_duplicates(subset="datetime")

            if (
                len(df_not_duplicate)
                == Consumption.objects.filter(user_id=user_id).count()
            ):
                continue

            df_not_duplicate["user_id"] = user_id
            Consumption.objects.bulk_create(
                Consumption(**row) for row in df_not_duplicate.to_dict("records")
            )

    def _upsert_total_consumption(self) -> None:
        CalculatedConsumption.objects.all().delete()
        consumptions = (
            Consumption.objects.annotate(date=TruncDay("datetime"))
            .values("date")
            .annotate(sum=Sum("consumption"))
        )
        df = pd.DataFrame(list(consumptions))
        CalculatedConsumption.objects.bulk_create(
            CalculatedConsumption(**row) for row in df.to_dict("records")
        )
