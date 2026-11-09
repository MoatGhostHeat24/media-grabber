# Changelog

All notable changes to MediaGrabber are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.2.0] — 2026-10-28

### Added
- Instagram Stories and Reels support, including carousel posts
- Clipboard monitoring mode (`clipboard_watch` in settings)
- `--max-height` and `--audio-format` CLI options
- Parallel download segments for YouTube (3–8 threads)
- Portuguese and Turkish interface translations

### Changed
- Filename template now supports `{date}` placeholder
- Reduced installer size by ~18%

### Fixed
- Facebook Watch links with query parameters failed to resolve
- Occasional freeze when a batch list contained an empty line
- X (Twitter) audio-only streams were silently skipped

## [1.1.2] — 2026-09-14

### Fixed
- Crash on Windows 10 1809 when the output folder was on a network drive
- Progress bar overflow for files larger than 4 GB

## [1.1.0] — 2026-08-02

### Added
- SoundCloud and Pinterest extractors
- Dark / light UI themes
- Auto-update check against GitHub releases

## [1.0.0] — 2026-06-20

- Initial public release
- YouTube, Instagram, Facebook, TikTok, X (Twitter), Vimeo, Reddit, Dailymotion
- Batch mode, audio extraction, filename templates
