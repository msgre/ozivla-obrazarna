from django.db import models
from django_extensions.db.models import TimeStampedModel

from common.uploads import UploadPath
from .grid import calculate_dimension


class Picture(TimeStampedModel):
    """
    Fotka obrazu, do ktereho se bude mapovat video s tvari.
    """
    title = models.CharField("Název", max_length=200)
    author = models.CharField("Autor", max_length=200)
    year = models.CharField("Datace", max_length=100)
    technique = models.CharField("Technika", max_length=100)
    collection = models.CharField("Sbírka", max_length=200, null=False, default="")
    number = models.CharField("Číslo", max_length=50, null=False, default="")
    notes = models.TextField("Poznámky", null=False, default="")
    width = models.IntegerField("Šířka repre obrazu", editable=False)
    height = models.IntegerField("Výška repre obrazu", editable=False)
    file = models.ImageField("Reprezentační obraz", upload_to=UploadPath("pictures"), height_field='height', width_field="width", max_length=255, help_text="PNG soubor, 720px na vysku, sirka jak vyjde")
    mask = models.ImageField("Maska", upload_to=UploadPath("masks"), max_length=255, help_text="PNG soubor s výřezem pro tvář, rozměr 1280x720 pixelů")

    class Meta:
        ordering = ['title']
        verbose_name = "Obraz"
        verbose_name_plural = "Obrazy"

    def __str__(self):
        return f'{self.title} ({self.year} {self.author})'

    def get_grid_parameter(self, idx):
        if not hasattr(self, '_grid'):
            self._grid = calculate_dimension(self.width, self.height)
        return self._grid[idx]

    @property
    def grid_width(self):
        return self.get_grid_parameter(0)

    @property
    def grid_height(self):
        return self.get_grid_parameter(1)

    @property
    def grid_ratio(self):
        return self.get_grid_parameter(2)
