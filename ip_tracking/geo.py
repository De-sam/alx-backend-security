# ip_tracking/geo.py
from __future__ import annotations
from typing import Optional, Tuple

import ipaddress
import requests


def _is_private_ip(ip: Optional[str]) -> bool:
    if not ip:
        return True
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return True


def lookup_ip(ip: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (country_iso2, city) for an IP or (None, None) if unknown.
    - Skips private/invalid IPs
    - Uses a simple, no-key provider by default for Task 2
    """
    if _is_private_ip(ip):
        return None, None

    try:
        # Free, no-auth option; replace with your preferred provider if needed.
        # Docs: https://ipapi.co/
        # Example: https://ipapi.co/8.8.8.8/json/
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=2.5)
        if resp.status_code != 200:
            return None, None
        data = resp.json() or {}
        country = (data.get("country") or "").strip() or None  # ISO-2 (e.g., "NG", "US")
        city = (data.get("city") or "").strip() or None
        return country, city
    except Exception:
        return None, None
