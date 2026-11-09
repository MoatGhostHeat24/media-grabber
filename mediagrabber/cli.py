"""Command-line interface for MediaGrabber."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from . import APP_NAME, __version__
from .downloader import DownloadOptions, download
from .platforms import PLATFORMS, detect, extract_urls

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=APP_NAME.lower(),
        description=f"{APP_NAME} — download video & audio from social platforms.",
    )
    parser.add_argument("urls", nargs="*", help="one or more media URLs")
    parser.add_argument("--batch", metavar="FILE", help="text file with one URL per line")
    parser.add_argument("-o", "--output", default="downloads", help="output directory")
    parser.add_argument("-t", "--template", dest="template",
                        default="{platform}/{title} [{id}].{ext}",
                        help="filename template ({platform},{title},{id},{ext},{date})")
    parser.add_argument("-a", "--audio-format", choices=["mp3", "m4a", "flac", "opus"],
                        help="extract audio instead of video")
    parser.add_argument("--max-height", type=int, metavar="PX",
                        help="cap video resolution, e.g. 720")
    parser.add_argument("-j", "--jobs", type=int, default=3, choices=range(1, 9),
                        help="parallel fragment downloads (default: 3)")
    parser.add_argument("--list-platforms", action="store_true",
                        help="show supported platforms and exit")
    parser.add_argument("-V", "--version", action="version",
                        version=f"{APP_NAME} {__version__}")
    return parser


def gather_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = list(args.urls)
    if args.batch:
        text = Path(args.batch).read_text(encoding="utf-8", errors="ignore")
        urls.extend(extract_urls(text))
    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def print_platforms() -> None:
    table = Table(title=f"{APP_NAME} supported platforms")
    table.add_column("Platform", style="cyan")
    table.add_column("Audio", justify="center")
    table.add_column("Stories / Reels", justify="center")
    for p in PLATFORMS:
        table.add_row(p.display_name, "yes" if p.supports_audio else "—",
                      "yes" if p.supports_stories else "—")
    console.print(table)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_platforms:
        print_platforms()
        return 0

    urls = gather_urls(args)
    if not urls:
        console.print("[yellow]No URLs given. Try:[/] mediagrabber <url> --help")
        return 2

    options = DownloadOptions(
        output_dir=Path(args.output),
        filename_template=args.template,
        audio_format=args.audio_format,
        max_height=args.max_height,
        max_parallel=args.jobs,
    )

    def on_progress(title: str, pct: float) -> None:
        console.print(f"\r[green]▸[/] {title[:60]}  {pct:5.1f}%", end="")

    results = download(urls, options, platform_for=detect, progress=on_progress)
    console.print()

    failed = 0
    for r in results:
        if r.ok:
            console.print(f"[green]✔[/] {r.platform}: saved to [bold]{r.filepath}[/]")
        else:
            failed += 1
            console.print(f"[red]✘[/] {r.url} — {r.error}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
