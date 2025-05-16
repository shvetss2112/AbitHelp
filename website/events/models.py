from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=1500)
    post_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField()
    source = models.ForeignKey("Resource", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events_images/', default='events_images/default.jpg')

    def __str__(self):
        return self.title


class Resource(models.Model):
    name = models.CharField(max_length=64, null=False)
    link = models.URLField()

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='subscribers')

    class Meta:
        unique_together = ('user', 'resource')

    def __str__(self):
        return f"{self.user.username} -> {self.resource.name}"
