from rest_framework import routers
from .views import EventViewSet, LikeView, UnlikeView, SubscriptionView, UnsubscribeView, GoogleLogin, ResourceViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'resources', ResourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('like/', LikeView.as_view(), name='like'),
    path('unlike/', UnlikeView.as_view(), name='unlike'),
    path('subscriptions/', SubscriptionView.as_view(), name='subscriptions'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('auth/google/', GoogleLogin.as_view(), name='google_login')
]
