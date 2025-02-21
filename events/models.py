from django.db import models


class Event(models.Model):
    content = models.TextField(max_length=1500)
    post_link = models.URLField()
    date = models.DateTimeField(null=True, blank=True)
    source = models.ForeignKey("Resource", on_delete=models.CASCADE)

    def __str__(self):
        return self.content if len(self.content) <= 10 else f"{self.content[:10]}..."


class Resource(models.Model):
    name = models.CharField(max_length=64, null=False)
    link = models.URLField()

    def __str__(self):
        return self.name
