from rest_framework import serializers


class PredictionInputSerializer(serializers.Serializer):
    BMI = serializers.FloatField(required=False)
    Smoking = serializers.CharField(required=False, allow_blank=True)
    AlcoholDrinking = serializers.CharField(required=False, allow_blank=True)
    Stroke = serializers.CharField(required=False, allow_blank=True)
    PhysicalHealth = serializers.IntegerField(required=False)
    MentalHealth = serializers.IntegerField(required=False)
    DiffWalking = serializers.CharField(required=False, allow_blank=True)
    Sex = serializers.CharField(required=False, allow_blank=True)
    AgeCategory = serializers.CharField(required=False, allow_blank=True)
    Diabetic = serializers.CharField(required=False, allow_blank=True)
    PhysicalActivity = serializers.CharField(required=False, allow_blank=True)
    GenHealth = serializers.CharField(required=False, allow_blank=True)
    SleepTime = serializers.IntegerField(required=False)
    Asthma = serializers.CharField(required=False, allow_blank=True)
    KidneyDisease = serializers.CharField(required=False, allow_blank=True)
    SkinCancer = serializers.CharField(required=False, allow_blank=True)
