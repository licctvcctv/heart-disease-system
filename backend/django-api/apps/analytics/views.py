from rest_framework.response import Response
from rest_framework.views import APIView

from .services import AnalysisService, ModelMetricsService, OverviewService


class OverviewView(APIView):
    def get(self, request):
        return Response(OverviewService.get_data())


class AgeAnalysisView(APIView):
    def get(self, request):
        return Response(AnalysisService.age_data())


class LifestyleAnalysisView(APIView):
    def get(self, request):
        return Response(AnalysisService.lifestyle_data())


class ClinicalAnalysisView(APIView):
    def get(self, request):
        return Response(AnalysisService.clinical_data())


class ModelMetricsView(APIView):
    def get(self, request):
        return Response(ModelMetricsService.get_data())
