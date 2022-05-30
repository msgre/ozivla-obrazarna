"""
TODO:
- mozna mit 2 ruzne serializery (list vs. detail)
- ty podrobnosti o FK objektech jsou pro list mozna az moc
"""

from rest_framework import serializers

from pictures.serializers import PictureSerializer
from accompaniments.serializers import AccompanimentSerializer
from .models import Performance
from pictures.models import Picture


class PerformanceSerializer(serializers.ModelSerializer):
    picture = PictureSerializer(read_only=True)
    accompaniment = AccompanimentSerializer(read_only=True)

    class Meta:
        model = Performance
        fields = ['id', 'state', 'picture', 'accompaniment', 'raw_footage', 'processed_footage', 'demonstrated_date', 'selected', 'created', 'modified']
        read_only_fields = ['state']


class PerformanceUploadSerializer(serializers.ModelSerializer):
    picture_id = serializers.IntegerField(required=False)
    accompaniment_id = serializers.IntegerField(required=False)

    class Meta:
        model = Performance
        fields = ['picture_id', 'accompaniment_id', 'raw_footage']
