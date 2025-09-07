# ip_tracking/tasks.py
from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.db.models import Count, Q
from django.utils import timezone

from .models import RequestLog, SuspiciousIP


@shared_task
def scan_for_suspicious_ips():
    """
    Hourly anomaly scanner:
    - Flag IPs with >100 requests in the last hour.
    - Flag IPs that accessed sensitive paths (/admin, /login, etc.).
    Idempotent-ish: uses get_or_create to avoid duplicate (ip, reason) rows.
    """
    cutoff = timezone.now() - timedelta(hours=1)
    base = RequestLog.objects.filter(timestamp__gte=cutoff).exclude(ip_address__isnull=True)

    # 1) High traffic (>100 reqs in last hour)
    high = (
        base.values("ip_address")
        .annotate(n=Count("id"))
        .filter(n__gt=100)
    )
    for row in high:
        ip = row["ip_address"]
        reason = f"High traffic: {row['n']} requests in last hour"
        SuspiciousIP.objects.get_or_create(ip_address=ip, reason=reason)

    # 2) Sensitive paths (customize as needed)
    sensitive_paths_exact = {"/admin", "/admin/", "/login", "/accounts/login"}
    sensitive_hits = (
        base.filter(
            Q(path__in=sensitive_paths_exact)
            | Q(path__startswith="/admin")
            | Q(path__icontains="login")
        )
        .values("ip_address", "path")
        .distinct()
    )
    for row in sensitive_hits:
        ip = row["ip_address"]
        path = row["path"]
        reason = f"Accessed sensitive path: {path}"
        SuspiciousIP.objects.get_or_create(ip_address=ip, reason=reason)
