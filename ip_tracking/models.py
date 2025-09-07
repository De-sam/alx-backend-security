# ip_tracking/models.py
from django.db import models


class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=2048)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["ip_address"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.ip_address} -> {self.path} @ {self.timestamp:%Y-%m-%d %H:%M:%S}"


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["ip_address"]),
        ]

    def __str__(self):
        return self.ip_address
