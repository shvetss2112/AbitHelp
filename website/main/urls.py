from django.urls import path

from . import views

urlpatterns = [
    path('', views.my_news, name='index'),
    path('about-us', views.about_us, name='about_us'),
    path('<int:id>', views.news_detail, name='news_detail')
]
