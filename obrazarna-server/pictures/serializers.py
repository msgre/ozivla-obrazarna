from rest_framework import serializers
from .models import Picture


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ['id', 'title', 'author', 'year', 'technique', 'collection', 'number', 'notes', 'file', 'mask', 'width', 'height', 'grid_width', 'grid_height', 'grid_ratio', 'created', 'modified']
