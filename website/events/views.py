from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Event, Like, EventImage, Subscription, Resource
from .serializers import EventSerializer, EventLikeSerializer, ResourceSerializer
from .permissions import IsAdminOrReadOnly
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .filters import EventAPIFilter


class GoogleLogin(SocialLoginView):
    permission_classes = [AllowAny]
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAdminOrReadOnly]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventAPIFilter

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

    def perform_create(self, serializer):
        event = serializer.save()
        images_data = self.request.FILES.getlist('images')
        for image_data in images_data:
            EventImage.objects.create(event=event, image=image_data)


class LikeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventLikeSerializer(data=request.data)
        if serializer.is_valid():
            event_id = serializer.validated_data['event_id']
            event = Event.objects.get(pk=event_id)
            like, created = Like.objects.get_or_create(user=request.user, event=event)
            if created:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnlikeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventLikeSerializer(data=request.data)
        if serializer.is_valid():
            event_id = serializer.validated_data['event_id']
            event = Event.objects.get(pk=event_id)
            Like.objects.filter(user=request.user, event=event).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        return Response([{'resource_id': sub.resource.id, 'resource_name': sub.resource.name} for sub in subscriptions])

    def post(self, request):
        resource_id = request.data.get('resource_id')
        try:
            resource = Resource.objects.get(pk=resource_id)
            Subscription.objects.create(user=request.user, resource=resource)
            return Response(status=status.HTTP_201_CREATED)
        except Resource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)


class UnsubscribeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        resource_id = request.data.get('resource_id')
        try:
            resource = Resource.objects.get(pk=resource_id)
            Subscription.objects.filter(user=request.user, resource=resource).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Resource.DoesNotExist:
            return Response({'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)