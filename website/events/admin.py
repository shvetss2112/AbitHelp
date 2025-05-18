from django.contrib import admin
from . import models


admin.site.register(models.Event)
admin.site.register(models.Resource)
admin.site.register(models.Subscription)
admin.site.register(models.EventImage)
