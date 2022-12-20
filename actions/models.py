from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Action(models.Model):
    """Хранение информации о действия пользователей"""
    user = models.ForeignKey(
        'auth.User',
        related_name='actions',
        db_index=True,
        on_delete=models.CASCADE,
        verbose_name='Пользователь который выполняет действие'
    )
    verb = models.CharField(max_length=255, verbose_name='какое действие выполнил пользователь')
    target_ct = models.ForeignKey(  # внешний ключ на модель ContentType
        ContentType,
        blank=True,
        null=True,
        related_name='target_obj',
        on_delete=models.CASCADE
    )
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)  # для хранения
    # идентификатора на связанный объект
    target = GenericForeignKey('target_ct', 'target_id')  # поле для обращения к связанному объекту на основании его
    # типа и ID
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)
