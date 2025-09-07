# ip_tracking/models.py
from django.db import models


class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=2048)

    # Task 2 fields
    country = models.CharField(max_length=2, null=True, blank=True)   # ISO-2 (e.g., "NG", "US")
    city = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["ip_address"]),
            models.Index(fields=["country"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        loc = f"{self.country or ''}/{self.city or ''}".strip("/")
        return f"{self.ip_address} -> {self.path} [{loc}] @ {self.timestamp:%Y-%m-%d %H:%M:%S}"


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["ip_address"]),
        ]

    def __str__(self):
        return self.ip_address
