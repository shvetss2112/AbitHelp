from rest_framework import serializers
from .models import Event, Resource
import uuid


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'content', 'title', 'images', 'post_link', 'date', 'source', 'is_liked', 'created_at']

    def get_is_liked(self, obj):
        liked_ids = self.context.get('liked_event_ids', set())
        return obj.id in liked_ids

    def get_images(self, obj):
        return [image.image.url for image in obj.images.all()]


class EventLikeSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()

    def validate_event_id(self, value):
        if not Event.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Event with this id does not exist.")
        return value