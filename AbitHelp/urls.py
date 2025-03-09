from django.contrib import admin
from django.urls import path, include
from api_auth.views import login as api_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('allauth.urls')),
    path('api-login/', api_login),
    path('api/', include('events.urls'))
]
