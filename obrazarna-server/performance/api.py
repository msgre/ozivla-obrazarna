from datetime import datetime
from django.utils import timezone
from django.utils.timezone import make_aware

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from common.utils import dict_subset
from .serializers import PerformanceSerializer, PerformanceUploadSerializer
from .models import Performance
from .tasks import process_footage



class PerformanceViewSet(viewsets.ModelViewSet):
    """
    API nad vystoupenimi lidi.
    """
    queryset = Performance.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.action == "create":
            return PerformanceUploadSerializer
        return PerformanceSerializer

    @action(detail=True, methods=['post'])
    def played(self, request, pk=None):
        """
        Oznaceni vystupu jako jiz prehraneho.
        """
        obj = Performance.objects.get(pk=pk)
        obj.selected = False
        obj.demonstrated_date = timezone.now()
        obj.save()
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'])
    def select(self, request, pk=None):
        """
        Oznaceni obrazu k promitnuti.
        """
        obj = Performance.objects.get(pk=pk)
        obj.selected = True
        obj.demonstrated_date = None
        obj.save()
        return Response({'status': 'ok'})

    @action(detail=False)
    def recommend(self, request):
        """
        Doporuci dalsi potrebne zdroje k novemu vystupu, tj. obraz a doprovod k nemu.

        Detaily viz Performance.recommend().
        """
        if (selected_pictures := request.GET.get('selected', None)):
            selected_pictures = [int(i) for i in selected_pictures.split(',')]
        recommended = Performance.recommend(selected_pictures=selected_pictures)

        obj = Performance(
            picture_id=recommended['picture'],
            accompaniment_id=recommended['accompaniment'],
        )
        serializer = self.get_serializer(obj)
        return Response(dict_subset(serializer.data, ['picture', 'accompaniment']))

    @action(detail=False)
    def upcomming(self, request):
        """
        Vrati data o vystupech pripravenych k projekci, a seznam par nedavno promitnutych.

        Detaily viz Performance.upcomming().
        """
        upcomming = Performance.upcomming()
        data = {
            'ready': PerformanceSerializer(upcomming['ready'], many=True).data,
            'selected': PerformanceSerializer(upcomming['selected'], many=True).data,
            'recent': PerformanceSerializer(upcomming['recent'], many=True).data,
        }
        return Response(data)

    @action(detail=False)
    def check(self, request):
        """
        TODO:
        - musi se hlidat i to ze se uz video prehralo
        """
        now = make_aware(datetime.fromtimestamp(int(request.GET['now'])/1000))
        qs = Performance.objects.filter(state__in=(Performance.STATE_READY, Performance.STATE_DEMONSTRATED), modified__gte=now)
        return Response({'actual': not qs.exists()})

    def perform_create(self, serializer):
        obj = serializer.save()
        process_footage.delay(obj.id)
