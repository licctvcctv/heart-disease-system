from django.urls import path

from .views import AgeAnalysisView, ClinicalAnalysisView, LifestyleAnalysisView


urlpatterns = [
    path("age", AgeAnalysisView.as_view()),
    path("lifestyle", LifestyleAnalysisView.as_view()),
    path("clinical", ClinicalAnalysisView.as_view()),
]
