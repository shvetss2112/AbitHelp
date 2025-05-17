from rest_framework import viewsets
from .models import Event, Like
from .serializers import EventSerializer
from .permissions import IsAdminOrReadOnly
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'date': ['gte', 'lte'],
    }
    search_fields = ['content', 'date']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if user.is_authenticated:
            liked_ids = set(
                Like.objects.filter(user=user).values_list('event_id', flat=True)
            )
        else:
            liked_ids = set()
        context['liked_event_ids'] = liked_ids
        return context
