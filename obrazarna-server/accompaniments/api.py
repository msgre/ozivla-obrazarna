from rest_framework import viewsets

from .serializers import AccompanimentSerializer
from .models import Accompaniment


class AccompanimentViewSet(viewsets.ModelViewSet):
    """
    API nad hudebnimi doprovody.
    """
    queryset = Accompaniment.objects.all()
    serializer_class = AccompanimentSerializer
