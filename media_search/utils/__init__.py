from .normalizers import normalize
from .sanitizers import sanitize

def normalize_and_sanitize(url):
    if url:
        return sanitize(normalize(url))
    return url
