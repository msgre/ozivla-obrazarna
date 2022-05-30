import logging
from django_rq import job

from .models import Performance


logger = logging.getLogger(__name__)


@job
def process_footage(performance_id):
    """
    Asynchronni konverze videa.

    Podrobnosti viz Performance.process_footage().
    """
    try:
        performance = Performance.objects.get(id=performance_id)
    except Performance.DoesNotExists:
        logger.warning('Nezname Performance.id=%s', performance_id)
        return False

    if not performance.raw_footage:
        logger.warning('Performance.id=%s neni zatim spojeno s zadnou nahravkou', performance_id)
        return False

    if performance.process_footage():
        logger.info('Performance.id=%s uspesne zprocesovano', performance_id)
    else:
        logger.error('Processing videa u Performance.id=%s nekde selhal', performance_id)
