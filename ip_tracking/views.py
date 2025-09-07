# ip_tracking/views.py
from __future__ import annotations

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ratelimit.core import is_ratelimited


def _rate_for(request) -> str:
    """10/min for authenticated, 5/min for anonymous."""
    return "10/m" if getattr(request, "user", None) and request.user.is_authenticated else "5/m"


def _too_many():
    return JsonResponse({"detail": "Rate limit exceeded. Try again soon."}, status=429)


@csrf_exempt
def login_view(request):
    """
    Example sensitive endpoint with rate limiting.
    - POST only (simulate login)
    - Key: user_or_ip (user id if logged in, else client IP)
    - Rate: dynamic based on auth state
    """
    # Enforce only on POST (typical for login submissions)
    limited = is_ratelimited(
        request=request,
        group="auth:login",
        key="user_or_ip",
        rate=_rate_for(request),
        method=["POST"],
        increment=True,  # count this attempt
    )
    if limited:
        return _too_many()

    if request.method != "POST":
        return HttpResponse("Use POST for login.", status=405)

    # ---- Your real login logic goes here ----
    # e.g., validate creds, set session/JWT, etc.
    # For the task, just return success to prove it works.
    return JsonResponse({"detail": "Login attempt accepted (demo)."}, status=200)
