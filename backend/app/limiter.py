import os

from slowapi import Limiter
from slowapi.util import get_remote_address

storage_uri = os.getenv("RATE_LIMIT_STORAGE_URI", "memory://")

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
)

RATE_BOARD_CREATE = "5/minute"
RATE_BOARD_FETCH = "10/minute"
RATE_CARD_VOTE = "10/minute"
