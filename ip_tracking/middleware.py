# ip_tracking/middleware.py
from __future__ import annotations

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from .models import RequestLog, BlockedIP


def _extract_client_ip(request) -> str | None:
    """
    Minimal IP extraction:
    - First item of X-Forwarded-For if present (typical behind proxies)
    - Fallback to REMOTE_ADDR
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        first = xff.split(",")[0].strip()
        return first or None
    return request.META.get("REMOTE_ADDR")


class IPLoggingMiddleware(MiddlewareMixin):
    """
    Task 1:
      - If request IP is in BlockedIP, return 403 Forbidden (no further handling).
    Task 0:
      - Otherwise, log IP + path + timestamp.
    """

    def process_request(self, request):
        ip = _extract_client_ip(request)

        # 1) Blacklist check
        try:
            if ip and BlockedIP.objects.filter(ip_address=ip).exists():
                return HttpResponseForbidden("Forbidden: Your IP has been blocked.")
        except Exception:
            # Fail-open on blacklist check issues (optional: log this with Sentry)
            pass

        # 2) Log request (Task 0)
        try:
            RequestLog.objects.create(ip_address=ip, path=request.path)
        except Exception:
            # Never crash the request because logging failed
            pass
