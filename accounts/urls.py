from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from . import views, forms

urlpatterns = [
    path('login/', forms.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
]
