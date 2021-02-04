import uuid

from django.db import models

class Modify(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Partnerweb3Mobile(Modify):
    release_version = models.CharField(max_length=10)
    description = models.TextField()
    url = models.URLField()

