from django.urls import path

from .views import (
    ClusterStatusView,
    ETLStepsView,
    PredictionHistoryView,
    WarehouseView,
)

urlpatterns = [
    path("warehouse", WarehouseView.as_view()),
    path("cluster", ClusterStatusView.as_view()),
    path("predictions", PredictionHistoryView.as_view()),
    path("etl-steps", ETLStepsView.as_view()),
]
