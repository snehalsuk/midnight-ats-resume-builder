"""Rate limiting for brute-force-sensitive endpoints (spec §37). Keyed by
client IP; limits are configurable via LOGIN_RATE_LIMIT / REGISTER_RATE_LIMIT
so they can be tuned per environment without a code change.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
