from django.db import models


class PredictionRecord(models.Model):
    probability = models.FloatField()
    risk_level = models.CharField(max_length=20)
    risk_label = models.CharField(max_length=20)
    model_name = models.CharField(max_length=50)
    input_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "system"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.risk_label} ({self.probability}) - {self.created_at}"
