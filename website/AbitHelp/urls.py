from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

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

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
