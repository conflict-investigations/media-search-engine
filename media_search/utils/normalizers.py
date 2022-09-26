# Normalize URLs to their canonical paths
# Also remove any URL schemas
# Makes it possible to e.g. match both of the following to the same entity:
# twitter.com/foo and mobile.twitter.com/foo

def normalize_url(url):
    return url.split('://', 1)[-1]

def normalize_twitter(url):
    TWITTER_CANONICAL = 'twitter.com'
    TWITTER_MOBILE = 'mobile.twitter.com'
    # TWITTER_LITE = 'm.twitter.com'  # ???
    if url.startswith(TWITTER_MOBILE):
        return url.replace(TWITTER_MOBILE, TWITTER_CANONICAL)
    return url


NORMALIZERS = [
    normalize_url,
    normalize_twitter,
]

def normalize(url):
    for n in NORMALIZERS:
        url = n(url)
    return url
