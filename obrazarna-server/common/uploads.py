import os
import time

from django.utils.deconstruct import deconstructible


@deconstructible
class UploadPath:
    """
    Pomocna trida, ktera dynamicky vygeneruje cestu pro uploadnute soubory.

    NOTE: zbytecna slozitost vynucena Django migracemi (puvodne jsem to mel realizovane
    jako funkci, ktera vracela funkci, ale pak nesla udelat initial migrace, koncilo
    to hlaskou "ValueError: Could not find function fn in common.uploads."
    """
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, instance, filename):
        now = time.time()
        name, ext = os.path.splitext(filename)
        return f"{self.prefix}/{name}_{str(now).replace('.', '_')}{ext}"
