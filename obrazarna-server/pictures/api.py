from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PictureSerializer
from .models import Picture
from .grid import (GRID_WIDTH, GRID_HEIGHT, PADDING, SCREEN_WIDTH, SCREEN_HEIGHT, CELL_WIDTH, CELL_HEIGHT)


class PictureViewSet(viewsets.ModelViewSet):
    """
    API nad obrazy.
    """
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


class DimensionsView(APIView):
    """
    TODO:
    """

    def get(self, request, format=None):
        data = {
            'grid': {
                'width': GRID_WIDTH,
                'height': GRID_HEIGHT,
                'padding': PADDING,
            },
            'cell': {
                'width': CELL_WIDTH,
                'height': CELL_HEIGHT,
            },
            'screen': {
                'width': SCREEN_WIDTH,
                'height': SCREEN_HEIGHT,
            },
        }
        return Response(data)
