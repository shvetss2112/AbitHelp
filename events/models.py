from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=1500)
    post_link = models.URLField()
    date = models.DateTimeField()
    source = models.ForeignKey("Resource", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Resource(models.Model):
    name = models.CharField(max_length=64, null=False)
    link = models.URLField()

    def __str__(self):
        return self.name
