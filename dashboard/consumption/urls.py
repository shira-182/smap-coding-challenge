from django.urls import path

from .views import SummaryDetail, SummaryView

urlpatterns = [
    path(r"", SummaryView.as_view()),
    path(r"summary/", SummaryView.as_view(), name="summary"),
    path(r"detail/<int:pk>", SummaryDetail.as_view(), name="detail"),
]
