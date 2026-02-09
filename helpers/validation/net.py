# helpers/validation/net.py
# Network-related validators (hostnames, IPs, ports, endpoints, URLs). Mapping helper is provided for consistent error paths.

from __future__ import annotations

import ipaddress
import re
from typing import Any, Optional
from urllib.parse import urlparse

from .errors import ValidationError, qpath
from .scalars import ensure_int, ensure_ip, ensure_str

_HOST_LABEL_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")


def ensure_port(v: Any, *, path: str = "port") -> int:
    """Ensure v is a valid TCP/UDP port (1..65535)."""
    return ensure_int(v, path=path, min_v=1, max_v=65535)


def ensure_host(v: Any, *, path: str = "host", allow_localhost: bool = True) -> str:
    """
    Ensure v is a host string: either an IP address or a hostname.

    This is intentionally conservative:
      - Rejects whitespace
      - Validates hostname label rules
      - Allows "localhost" by default
    """
    s = ensure_str(v, path=path, allow_empty=False)

    if allow_localhost and s.lower() == "localhost":
        return "localhost"

    # IP is acceptable.
    try:
        ipaddress.ip_address(s)
        return s
    except Exception:
        pass

    # Hostname validation (basic, RFC-ish).
    if len(s) > 253:
        raise ValidationError(f"{qpath(path)} hostname too long (got len={len(s)})")

    labels = s.split(".")
    if any(not lbl for lbl in labels):
        raise ValidationError(f"{qpath(path)} must be a valid hostname (empty label in {s!r})")

    for lbl in labels:
        if not _HOST_LABEL_RE.match(lbl):
            raise ValidationError(f"{qpath(path)} must be a valid hostname (bad label {lbl!r})")

    return s


def ensure_endpoint(v: Any, *, path: str = "endpoint") -> tuple[str, int]:
    """
    Ensure v is an endpoint string and return (host, port).

    Supported forms:
      - "host:1234"
      - "[::1]:1234" (IPv6 in brackets)
    """
    s = ensure_str(v, path=path, allow_empty=False)

    host: str
    port_s: str

    if s.startswith("["):
        # IPv6 bracket form: [addr]:port
        if "]" not in s:
            raise ValidationError(f"{qpath(path)} must be in form '[ipv6]:port' (got {s!r})")
        close = s.index("]")
        host = s[1:close]
        rest = s[close + 1 :]
        if not rest.startswith(":"):
            raise ValidationError(f"{qpath(path)} must be in form '[ipv6]:port' (got {s!r})")
        port_s = rest[1:]
        host = ensure_ip(host, path=f"{path}.host", version=6)
    else:
        # Split on last ":" to allow hostnames containing ":" only via IPv6 bracket form.
        if ":" not in s:
            raise ValidationError(f"{qpath(path)} must be in form 'host:port' (got {s!r})")
        host, port_s = s.rsplit(":", 1)
        host = ensure_host(host, path=f"{path}.host")

    try:
        port = ensure_port(int(port_s), path=f"{path}.port")
    except Exception as e:
        raise ValidationError(f"{qpath(path)} invalid port in endpoint (got {s!r})") from e

    return host, port


def ensure_http_url(v: Any, *, path: str = "url") -> str:
    """
    Ensure v is an http(s) URL.

    This is a basic structural check suitable for config validation.
    """
    s = ensure_str(v, path=path, allow_empty=False)
    u = urlparse(s)
    if u.scheme not in {"http", "https"}:
        raise ValidationError(f"{qpath(path)} must start with http:// or https:// (got {s!r})")
    if not u.netloc:
        raise ValidationError(f"{qpath(path)} must include a host (got {s!r})")
    return s


def _require_ip_value(v: Any, *, p: str, version: Optional[int]) -> str:
    """
    Internal helper for mapping.require_ip().

    p is already the joined path string used by mapping readers; we quote it consistently.
    """
    return ensure_ip(v, path=p, version=version)
