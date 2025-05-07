from rest_framework import serializers
from .models import Event
import uuid


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'content', 'title', 'image', 'post_link', 'date', 'source']
        