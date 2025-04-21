from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Event
from django.db import connection


@receiver(post_save, sender=Event)
def event_post_save(sender, instance, created, **kwargs):
    if created:
        with connection.cursor() as cursor:
            cursor.execute("NOTIFY events_channel, '%s';", [instance.id])
