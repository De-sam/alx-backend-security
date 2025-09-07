# ip_tracking/middleware.py
from __future__ import annotations

from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from .models import RequestLog, BlockedIP
from . import geo


CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hours


def _extract_client_ip(request) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        first = xff.split(",")[0].strip()
        return first or None
    return request.META.get("REMOTE_ADDR")


class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = _extract_client_ip(request)

        # 1) Blacklist check (Task 1)
        try:
            if ip and BlockedIP.objects.filter(ip_address=ip).exists():
                return HttpResponseForbidden("Forbidden: Your IP has been blocked.")
        except Exception:
            # Fail-open on blacklist check issues
            pass

        # 2) Geolocation with cache (Task 2)
        country, city = None, None
        try:
            cache_key = f"geo:{ip}"
            cached = cache.get(cache_key) if ip else None
            if cached:
                country, city = cached.get("country"), cached.get("city")
            else:
                country, city = geo.lookup_ip(ip)
                if ip:
                    cache.set(cache_key, {"country": country, "city": city}, CACHE_TTL_SECONDS)
        except Exception:
            # If geo lookup or cache fails, just proceed without it.
            pass

        # 3) Log request (Task 0 + Task 2 enrichment)
        try:
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path,
                country=country,
                city=city,
            )
        except Exception:
            # Never crash the request because logging failed
            pass
