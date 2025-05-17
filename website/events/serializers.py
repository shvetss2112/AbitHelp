from rest_framework import serializers
from .models import Event
import uuid


class EventSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'content', 'title', 'image', 'post_link', 'date', 'source', 'is_liked', 'created_at']

    def get_is_liked(self, obj):
        liked_ids = self.context.get('liked_event_ids', set())
        return obj.id in liked_ids
