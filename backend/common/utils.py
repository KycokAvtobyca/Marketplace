import os

from django.utils.deconstruct import deconstructible
from slugify import slugify


@deconstructible
class UploadPath:
    def __init__(self, prefix=""):
        self.prefix = prefix

    def __call__(self, instance, filename):
        folder = slugify(instance.name) or f"{self.prefix}_{instance.pk}"
        return os.path.join(self.prefix, folder, filename)
