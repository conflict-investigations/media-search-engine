# Strip query strings and tracking info from links

def sanitize_url(url):
    pass

def sanitize_tiktok(url):
    # Remove tracking/query strings in Tiktok URLs
    TIKTOK_WWW = "www.tiktok.com"
    if url.startswith(TIKTOK_WWW):
        return url.split('?')[0]
    return url

def sanitize_twitter(url):
    # Removing tracking, but not in search queries
    TWITTER = 'twitter.com'
    SEARCH = 'twitter.com/search?'
    if url.startswith(TWITTER) and not url.startswith(SEARCH):
        return url.split('?')[0]
    return url


SANITIZERS = [
    sanitize_tiktok,
    sanitize_twitter,
]

def sanitize(url):
    for s in SANITIZERS:
        url = s(url)
    return url
