from django.db import models


class Source(models.Model):
    domain = models.CharField(unique=True, max_length=512)
    name = models.CharField(max_length=1024)


class Article(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=1024)
    snippet = models.CharField(max_length=2048)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="articles")