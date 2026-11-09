"""Core download engine. Thin wrapper around yt-dlp with sane defaults."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

import yt_dlp

from . import APP_NAME, __version__, USER_AGENT
from .platforms import Platform


ProgressFn = Callable[[str, float], None]


@dataclass
class DownloadOptions:
    output_dir: Path = Path("downloads")
    filename_template: str = "{platform}/{title} [{id}].{ext}"
    audio_format: str | None = None      # mp3 / m4a / flac / opus / None
    max_height: int | None = None        # cap video resolution
    max_parallel: int = 3
    user_agent: str = USER_AGENT
    quiet: bool = False


@dataclass
class DownloadResult:
    url: str
    platform: str
    title: str = ""
    filepath: Path | None = None
    ok: bool = False
    error: str | None = None
    logs: list[str] = field(default_factory=list)


def _format_from_template(template: str, platform: Platform) -> str:
    return str(
        Path(template)
        .replace("{platform}", platform.key)
        .replace("{platform_name}", platform.display_name)
    )


def build_ydl_opts(options: DownloadOptions, platform: Platform,
                   progress: ProgressFn | None = None) -> dict:
    outtmpl = _format_from_template(options.filename_template, platform)
    opts: dict = {
        "outtmpl": str(options.output_dir / (outtmpl + ".%(ext)s")),
        "noplaylist": False,
        "concurrent_fragment_downloads": max(1, options.max_parallel),
        "quiet": options.quiet,
        "no_warnings": options.quiet,
        "retries": 5,
        "fragment_retries": 5,
        "http_headers": {"User-Agent": options.user_agent},
        "progress_hooks": ([lambda d: _on_progress(d, platform, progress)]
                           if progress else []),
    }

    if options.audio_format:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": options.audio_format,
            "preferredquality": "192",
        }]
    elif options.max_height:
        opts["format"] = f"best[height<={options.max_height}]/best"
    else:
        opts["format"] = "bestvideo*+bestaudio/best"
        opts["merge_output_format"] = "mp4"

    return opts


def _on_progress(payload: dict, platform: Platform, progress: ProgressFn | None) -> None:
    if progress is None:
        return
    status = payload.get("status", "")
    if status == "downloading":
        total = payload.get("total_bytes") or payload.get("total_bytes_estimate") or 0
        done = payload.get("downloaded_bytes", 0)
        pct = (done / total * 100.0) if total else 0.0
        progress(payload.get("info_dict", {}).get("title", platform.key), pct)
    elif status == "finished":
        progress(payload.get("info_dict", {}).get("title", platform.key), 100.0)


def download(urls: Iterable[str], options: DownloadOptions,
             platform_for: Callable[[str], Platform],
             progress: ProgressFn | None = None) -> list[DownloadResult]:
    results: list[DownloadResult] = []
    for url in urls:
        platform = platform_for(url)
        if platform is None:
            results.append(DownloadResult(url=url, platform="unknown",
                                          ok=False, error="Unsupported URL"))
            continue
        result = DownloadResult(url=url, platform=platform.key)
        try:
            with yt_dlp.YoutubeDL(build_ydl_opts(options, platform, progress)) as ydl:
                info = ydl.extract_info(url, download=True)
                result.title = info.get("title", "")
                result.filepath = Path(info.get("requested_downloads", [{}])[0]
                                       .get("filepath", ""))
                result.ok = True
        except yt_dlp.utils.DownloadError as exc:
            result.error = str(exc).splitlines()[-1]
        except Exception as exc:  # pragma: no cover - defensive
            result.error = f"{type(exc).__name__}: {exc}"
        results.append(result)
    return results


def probe(url: str) -> dict:
    """Fetch metadata without downloading."""
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True,
                           "http_headers": {"User-Agent": USER_AGENT}}) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "formats": len(info.get("formats") or []),
        "extractor": info.get("extractor_key"),
    }


if __name__ == "__main__":  # manual smoke test
    print(json.dumps(probe("https://vimeo.com/76979871"), indent=2))
    print(f"{APP_NAME} v{__version__}")
