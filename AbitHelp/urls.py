from django.contrib import admin
from django.urls import path, include

import main.views
import event_calendar.views
from api_auth.views import login as api_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('calendar/', include('event_calendar.urls')),
    path('accounts/', include('allauth.urls')),
    path('api-login/', api_login),
    path('api/', include('events.urls'))
]
