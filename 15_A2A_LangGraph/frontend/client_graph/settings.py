import os


def get_base_url() -> str:
    """Return the A2A server base URL.

    Defaults to http://localhost:10000, override via FRONTEND_A2A_BASE_URL.
    """
    return os.getenv("FRONTEND_A2A_BASE_URL", "http://localhost:10000")


def get_timeout_seconds() -> float:
    """Return HTTP timeout seconds for A2A calls (default 60)."""
    value = os.getenv("A2A_HTTP_TIMEOUT_SECONDS", "60")
    try:
        return float(value)
    except ValueError:
        return 60.0


