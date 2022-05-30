import os
import logging
import subprocess
import tempfile
from itertools import chain

from django.db import models
from django.db.models import Value, F, Count
from django_extensions.db.models import TimeStampedModel
from django.core.files import File

from common.uploads import UploadPath
from common.utils import check_attributes, get_least_used
from accompaniments.models import Accompaniment
from pictures.models import Picture


logger = logging.getLogger(__name__)


class Performance(TimeStampedModel):
    """
    Vystoupeni konkretniho cloveka, ktery se snazi ozivit vybrany obraz.
    """
    STATE_INITIAL = 'initial'
    STATE_RAW = 'raw'
    STATE_ERROR = 'error'
    STATE_READY = 'ready'
    STATE_DEMONSTRATED = 'demonstrated'
    STATE_CHOICES = (
        (STATE_INITIAL, '(1/4) Výchozí'),
        (STATE_RAW, '(2/4) Hrubá nahrávka'),
        (STATE_READY, '(3/4) Připraveno'),
        (STATE_DEMONSTRATED, '(4/4) Odprezentováno'),
        (STATE_ERROR, 'Chyba'),
    )

    picture = models.ForeignKey('pictures.Picture', verbose_name="Obraz", on_delete=models.SET_NULL, null=True, blank=True)
    accompaniment = models.ForeignKey('accompaniments.Accompaniment', verbose_name="Doprovod", on_delete=models.SET_NULL, null=True, blank=True)
    raw_footage = models.FileField("Hrubá nahrávka", upload_to=UploadPath('raw'), blank=True, default="")
    processed_footage = models.FileField("Zprocesovaná nahrávka", upload_to=UploadPath('processed'), blank=True, default="")
    processed_stdout = models.TextField("Processing STDOUT", blank=True, default="", editable=False)
    processed_stderr = models.TextField("Processing STDERR", blank=True, default="", editable=False)
    processed_returncode = models.IntegerField("Processing return code", null=True, default=None, editable=False)
    state = models.CharField("Stav", max_length=20, choices=STATE_CHOICES, default=STATE_INITIAL, editable=False)
    demonstrated_date = models.DateTimeField("Datum prezentace", blank=True, null=True)
    selected = models.BooleanField("Kandidát na projekci", default=False)


    class Meta:
        ordering = ['-created']
        verbose_name = "Vystoupení"
        verbose_name_plural = "Vystoupení"

    def __str__(self):
        return f'{self.picture} on {self.created}'

    @classmethod
    def get_counts(cls, model, attribute, selected=None):
        """
        Vrati statisticke udaje o tom, jak moc jsou v Performance modelu vyuzity zaznamy z `model`.

        Napr.:
            In [1]: get_counts(Picture, "picture_id")
            Out[1]: {1: 1, 2: 0, 3: 0}

        Pokud je zadan nepovinny parametr selected v podobe seznamu ID, pak se do vystupu dostanou
        je vybrane zaznamy. Tohle slouzi k tomu, aby se doporucil nektery z obrazku, ktery se vyskytuje
        na obrazovce s prehledem (intro faze).
        """
        # nejprve vytahneme statistiku o "attribute" z Performance modelu
        existing_counts = cls.objects.exclude(**{f'{attribute}__isnull': True}).values(attribute).annotate(count=Count(attribute)).order_by()

        # a pak doplnime jeste nepouzite zaznamy z modelu "model"
        nonexisting_counts = model.objects.exclude(id__in=[i[attribute] for i in existing_counts]).values(**{attribute: F('id')}).annotate(count=Value(0)).order_by()

        return {i[attribute]: i['count'] for i in chain(existing_counts, nonexisting_counts) if not selected or i[attribute] in selected}

    @classmethod
    def recommend(cls, selected_pictures=None):
        """
        Vrati ID doporucenych modelu pro dalsi vystoupeni, napr.:

            In [5]: Performance.recommend()
            Out[5]: {'picture': 3, 'accompaniment': 1}
        """
        picture_counts = cls.get_counts(Picture, "picture_id", selected_pictures)
        accompaniment_counts = cls.get_counts(Accompaniment, "accompaniment_id")

        return {
            'picture': get_least_used(picture_counts),
            'accompaniment': get_least_used(accompaniment_counts),
        }       

    @classmethod
    def upcomming(cls, recent_count=10):
        """
        Vrati zaznamy k rizeni projekce:

        {
            'ready': <Performances>,
            'selected': <Performances>,
            'recent': <Performances>,
        }

        kde

            ready -- je seznam vystupu ktere je mozne promitat
            selected -- selected je vystup ktery byl explicitne vybran obsluhou
            recent -- seznam nedavno promitnutych projekci
        """
        ready = cls.objects.filter(state=cls.STATE_READY).order_by('created')
        selected = ready.filter(selected=True).order_by('modified')
        ready = ready.exclude(id__in=selected.values_list('id', flat=True))
        recent = cls.objects.filter(state=cls.STATE_DEMONSTRATED).order_by('-demonstrated_date')[:recent_count]
        return {
            'ready': ready,
            'selected': selected,
            'recent': recent,
        }

    def resolve_state(self):
        """
        Podle atributu nastavenych u objektu rozpozna stav objektu.
        """
        if self.processed_returncode is not None and self.processed_returncode > 0:
            return self.STATE_ERROR

        if self.demonstrated_date:
            return self.STATE_DEMONSTRATED

        if check_attributes(self, ['picture', 'accompaniment', 'raw_footage', 'processed_footage']):
            return self.STATE_READY

        if self.raw_footage:
            return self.STATE_RAW

        return self.STATE_INITIAL

    def save(self, *args, **kwargs):
        """
        Postara se o automaticke nastaveni .state atributu.
        """
        self.state = self.resolve_state()
        return super().save(*args, **kwargs)

    def process_footage(self):
        """
        Zkonvertuje syrove vstupni video na proper h.264 mp4, ktery je mozne prehrat v prohlizeci.

        Nevim proc, ale to co vytvori picamera nejde v prohlizeci prehrat. Kdyz se to ale prozene
        pres ffmpeg, tak uz je to v cajku.
        """
        # vytvori prazdny soubor v /tmp adresari
        _, path = tempfile.mkstemp(suffix='.mp4')

        # prekonvertuje video
        cmd = ['ffmpeg', '-y', '-i', self.raw_footage.path, '-vcodec', 'libx264', path]
        completed = subprocess.run(cmd, capture_output=True)
        self.processed_returncode = completed.returncode
        self.processed_stdout = completed.stdout.decode('utf-8')
        self.processed_stderr = completed.stderr.decode('utf-8')

        try:
            completed.check_returncode()
        except subprocess.CalledProcessError:
            # cosik se pokazilo
            self.save()
            logger.error('Konvertovani souboru %s ze zaznamu Performance.id=%s selhalo', self.raw_footage.path, self.id)
            return False

        # nahrajem zkonvertovany soubor do Djanga
        with open(path, 'rb') as f:
            self.processed_footage = File(f, name=os.path.basename(path))
            self.processed_returncode = completed.returncode
            self.processed_stdout = completed.stdout.decode('utf-8')
            self.processed_stderr = completed.stderr.decode('utf-8')
            self.save()

        # smazem temp file
        os.remove(path)

        return True
