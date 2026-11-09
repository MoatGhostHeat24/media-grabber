"""Platform detection and URL normalization."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    key: str
    display_name: str
    pattern: re.Pattern[str]
    supports_audio: bool = True
    supports_stories: bool = False


PLATFORMS: tuple[Platform, ...] = (
    Platform(
        key="youtube",
        display_name="YouTube",
        pattern=re.compile(
            r"https?://(?:www\.|m\.|music\.)?"
            r"(?:youtube\.com/(?:watch\?v=|shorts/|playlist\?list=|embed/)"
            r"|youtu\.be/[\w\-]+)",
            re.IGNORECASE,
        ),
    ),
    Platform(
        key="instagram",
        display_name="Instagram",
        pattern=re.compile(
            r"https?://(?:www\.)?instagram\.com/"
            r"(?:p/|reel/|reels/|tv/|stories/)[\w\-.]+/?",
            re.IGNORECASE,
        ),
        supports_stories=True,
    ),
    Platform(
        key="facebook",
        display_name="Facebook",
        pattern=re.compile(
            r"https?://(?:www\.|web\.|m\.)?facebook\.com/"
            r"(?:watch/?\?v=|reel/|photo(?:\.php)?|share/[rv]/|.+?/videos/)",
            re.IGNORECASE,
        ),
        supports_stories=True,
    ),
    Platform(
        key="tiktok",
        display_name="TikTok",
        pattern=re.compile(
            r"https?://(?:www\.|vm\.|vt\.)?tiktok\.com/[\w@/\-.]+",
            re.IGNORECASE,
        ),
        supports_stories=True,
    ),
    Platform(
        key="twitter",
        display_name="X (Twitter)",
        pattern=re.compile(
            r"https?://(?:www\.)?(?:twitter|x)\.com/\w+/status/\d+",
            re.IGNORECASE,
        ),
    ),
    Platform(
        key="vimeo",
        display_name="Vimeo",
        pattern=re.compile(r"https?://(?:www\.)?vimeo\.com/\d+", re.IGNORECASE),
    ),
    Platform(
        key="soundcloud",
        display_name="SoundCloud",
        pattern=re.compile(r"https?://(?:www\.)?soundcloud\.com/[\w\-/]+", re.IGNORECASE),
    ),
    Platform(
        key="pinterest",
        display_name="Pinterest",
        pattern=re.compile(r"https?://(?:[\w]+\.)?pinterest\.[\w.]+/pin/\d+", re.IGNORECASE),
    ),
    Platform(
        key="reddit",
        display_name="Reddit",
        pattern=re.compile(r"https?://(?:www\.|v\.)?reddit\.com/r/\w+/comments/[\w]+", re.IGNORECASE),
    ),
    Platform(
        key="dailymotion",
        display_name="Dailymotion",
        pattern=re.compile(r"https?://(?:www\.)?dailymotion\.com/video/\w+", re.IGNORECASE),
    ),
)


def detect(url: str) -> Platform | None:
    """Return the platform matching *url*, or ``None`` if unsupported."""
    url = url.strip()
    for platform in PLATFORMS:
        if platform.pattern.match(url):
            return platform
    return None


def extract_urls(text: str) -> list[str]:
    """Pull every supported URL out of an arbitrary blob of text."""
    urls: list[str] = []
    for raw in re.split(r"[\s,;]+", text):
        if not raw:
            continue
        if not raw.startswith("http"):
            raw = "https://" + raw
        if detect(raw):
            urls.append(raw)
    return urls
