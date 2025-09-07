# ip_tracking/middleware.py
from __future__ import annotations
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog


def _extract_client_ip(request) -> str | None:
    """
    Minimal, dependency-free IP extraction:
    - Trust the first item in X-Forwarded-For if present (typical behind a proxy/load balancer).
    - Fallback to REMOTE_ADDR.
    NOTE: For production behind proxies, set Django's SECURE_PROXY_SSL_HEADER and
          USE X-Forwarded-For correctly or use django-ipware later.
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # XFF like: "client, proxy1, proxy2"
        first = xff.split(",")[0].strip()
        return first or None
    return request.META.get("REMOTE_ADDR")


class IPLoggingMiddleware(MiddlewareMixin):
    """
    Logs IP, timestamp, and path for every incoming request.
    Keep it lightweight to avoid request latency.
    """

    def process_request(self, request):
        ip = _extract_client_ip(request)
        path = request.path

        # Skip extremely noisy or irrelevant paths if you like:
        # if path.startswith(("/static/", "/media/")):
        #     return

        # Create the log row. This is a tiny write; acceptable for Task 0.
        # (We’ll discuss batching/Redis later in perf best practices.)
        try:
            RequestLog.objects.create(ip_address=ip, path=path)
        except Exception:
            # Fail-open: never break requests because logging failed.
            pass
