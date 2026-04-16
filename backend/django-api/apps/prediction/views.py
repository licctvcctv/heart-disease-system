import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PredictionInputSerializer
from .services import PredictionService

logger = logging.getLogger(__name__)


class PredictView(APIView):
    def post(self, request):
        serializer = PredictionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = PredictionService.predict(serializer.validated_data)

        # Save prediction record
        try:
            from apps.system.models import PredictionRecord

            PredictionRecord.objects.create(
                probability=result.get("probability", 0.0),
                risk_level=result.get("riskLevel", ""),
                risk_label=result.get("riskLabel", ""),
                model_name=result.get("model", ""),
                input_data=serializer.validated_data,
            )
        except Exception as exc:
            logger.warning("Failed to save PredictionRecord: %s", exc)

        return Response(result, status=status.HTTP_200_OK)
