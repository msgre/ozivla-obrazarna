from django.db import models
from django_extensions.db.models import TimeStampedModel

from common.uploads import UploadPath


class Accompaniment(TimeStampedModel):
    """
    Kratky hudebni doprovod, ktery se prilozi k vysledne nahravce performera
    (aby to melo stavu).
    """
    title = models.CharField("Název", max_length=200)
    author = models.CharField("Autor", max_length=200)
    file = models.FileField("Soubor", upload_to=UploadPath('accompaniments'), max_length=255, help_text="MP3 (?) soubor, max 10 vteřin dlouhý; kvalita?")

    class Meta:
        ordering = ['title']
        verbose_name = "Doprovod"
        verbose_name_plural = "Doprovody"

    def __str__(self):
        return f'{self.title} ({self.author})'
