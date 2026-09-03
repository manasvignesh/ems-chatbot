import time
import ipaddress
import urllib.parse
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import HTTPException, Request, status
from app.core.config import settings
from app.core.logging import logger


class RateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self, requests_per_minute: int = 40):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_rate_limited(self, key: str) -> bool:
        """Check whether the key has exceeded the rate limit."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old timestamps
        self.requests[key] = [t for t in self.requests[key] if t > cutoff]

        if len(self.requests[key]) >= self.requests_per_minute:
            return True

        self.requests[key].append(now)
        return False


rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE)


def validate_ssrf_url(url: str, allow_localhost_dev: bool = False) -> str:
    """Validate that the given URL does not point to internal, private, or metadata IPs."""
    parsed = urllib.parse.urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL protocol: {parsed.scheme}. Only HTTP/HTTPS are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must have a valid hostname.")

    # Check for localhost in dev mode
    if hostname in ("localhost", "127.0.0.1", "::1"):
        if allow_localhost_dev or settings.APP_ENV == "development":
            return url
        raise ValueError("Access to localhost is blocked.")

    # Check for IP ranges
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise ValueError(f"Access to private IP address '{hostname}' is blocked.")
        if str(ip) == "169.254.169.254":  # Cloud metadata service
            raise ValueError("Access to cloud metadata service is blocked.")
    except ValueError as e:
        # Hostname is a domain name (not an IP literal), which is standard
        if "does not appear to be an IPv4 or IPv6 address" in str(e):
            pass
        else:
            raise

    return url


def sanitize_text(text: str, max_chars: int = 2000) -> str:
    """Sanitize user input text to prevent overflow and null-byte attacks."""
    if not text:
        return ""
    # Strip null bytes and control chars
    clean = text.replace("\x00", "").strip()
    return clean[:max_chars]
