from django.urls import path

from . import views

urlpatterns = [
    path('', views.my_news, name='index'),
    path('about-us', views.about_us, name='about_us'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('<int:id>', views.news_detail, name='news_detail'),
    path('subscribe/<int:resource_id>/', views.subscribe_resource, name='subscribe_reousrce'),
    path('unsubscribe/<int:resource_id>/', views.unsubscribe_resource, name='unsubscribe_resource'),
    path('handle-like/<int:event_id>', views.handle_like, name='handle_like')
]
