from mediagrabber.platforms import detect, extract_urls


def test_detect_youtube():
    p = detect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert p is not None and p.key == "youtube"


def test_detect_youtu_be():
    p = detect("https://youtu.be/dQw4w9WgXcQ")
    assert p is not None and p.key == "youtube"


def test_detect_instagram_reel():
    p = detect("https://www.instagram.com/reel/Cx1y2z3AbCd/")
    assert p is not None and p.key == "instagram"


def test_detect_facebook_watch():
    p = detect("https://www.facebook.com/watch/?v=1234567890")
    assert p is not None and p.key == "facebook"


def test_detect_twitter_x():
    p = detect("https://x.com/someuser/status/1740000000000000000")
    assert p is not None and p.key == "twitter"


def test_unknown_url_returns_none():
    assert detect("https://example.com/video/123") is None


def test_extract_urls_from_text():
    blob = """
    check these out:
    https://youtu.be/abc123 and
    https://www.tiktok.com/@user/video/7300000000000000000
    not-a-link example.org
    """
    urls = extract_urls(blob)
    assert len(urls) == 2
    assert all(u.startswith("https://") for u in urls)
