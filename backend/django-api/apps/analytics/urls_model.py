from django.urls import path

from .views import ModelMetricsView


urlpatterns = [
    path("metrics", ModelMetricsView.as_view()),
]
