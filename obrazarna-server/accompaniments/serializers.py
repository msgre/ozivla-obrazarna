from rest_framework import serializers
from .models import Accompaniment


class AccompanimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accompaniment
        fields = ['id', 'title', 'author', 'file', 'created', 'modified']
