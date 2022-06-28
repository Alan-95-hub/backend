import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """Описание моделей для базы данных"""
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    parentId = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True)
    price = models.IntegerField(default=0, blank=True)

    class Type(models.TextChoices):
        OFFER = 'OFFER', _('OFFER')
        GRADUATE = 'CATEGORY', _('CATEGORY')
    type = models.CharField(max_length=100, choices=Type.choices)

    def __str__(self):
        return self.id


class ProductHistory(models.Model):
    """Описание истории модели"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    oldId = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    parentId = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    price = models.IntegerField(default=0, blank=True)

    class Type(models.TextChoices):
        OFFER = 'OFFER', _('OFFER')
        GRADUATE = 'CATEGORY', _('CATEGORY')
    type = models.CharField(max_length=100, choices=Type.choices)

    def __str__(self):
        return self.name
