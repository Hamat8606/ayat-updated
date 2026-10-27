#!/usr/bin/env python3
"""Generate per-ayah Russian MP3 files from the translation embedded in index.html.

This is an offline preparation tool, not part of the browser app. It does not
modify index.html and defaults to generating only Al-Fatiha for safe testing.

Requirements:
    python -m pip install edge-tts

Example:
    python tools/generate_ru_audio.py --surah 1
    python tools/generate_ru_audio.py --surah 1 --voice ru-RU-SvetlanaNeural
    python tools/generate_ru_audio.py --all

Generated files:
    generated-audio/ru/<surah>/<ayah>.mp3
    generated-audio/manifest.json

The audio is pre-generated speech, so phones only play MP3 files; they do not
run speech synthesis at playback time. Edge TTS is an online service, so this
script needs internet access while generating files.
"""
from __future__ import annotations

import argparse
import asyncio
import html
import json
import re
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "index.html"
OUT_DIR = ROOT / "generated-audio"
DEFAULT_VOICE = "ru-RU-SvetlanaNeural"


def load_verses():
    source = HTML_FILE.read_text(encoding="utf-8")
    match = re.search(
        r'<script\s+type="application/json"\s+id="d">([\s\S]*?)</script>',
        source,
    )
    if not match:
        raise RuntimeError('Could not find the embedded Quran data block (id="d").')
    rows = json.loads(html.unescape(match.group(1)))
    verses = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 4:
            continue
        surah, ayah, _arabic, translation = row[:4]
        translation = str(translation).strip()
        if translation:
            verses.append({"surah": int(surah), "ayah": int(ayah), "text": translation})
    if not verses:
        raise RuntimeError("No translation verses were found.")
    return verses


async def generate_one(verse, voice, destination, retries=3):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 1000:
        return "cached"
    last_error = None
    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(verse["text"], voice)
            await communicate.save(str(destination))
            if destination.exists() and destination.stat().st_size > 1000:
                return "generated"
            raise RuntimeError("TTS returned an empty or unexpectedly small file")
        except Exception as exc:
            last_error = exc
            await asyncio.sleep(1.5 * (attempt + 1))
    raise RuntimeError(
        f"Failed at {verse['surah']}:{verse['ayah']} after {retries} attempts: {last_error}"
    )


async def main_async(args):
    verses = load_verses()
    if args.surah is not None:
        verses = [v for v in verses if v["surah"] == args.surah]
    if args.limit:
        verses = verses[: args.limit]
    if not verses:
        raise RuntimeError("No verses selected. Check --surah.")

    manifest_path = OUT_DIR / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            manifest = {}

    total = len(verses)
    for index, verse in enumerate(verses, start=1):
        dest = OUT_DIR / "ru" / str(verse["surah"]) / f"{verse['ayah']}.mp3"
        status = await generate_one(verse, args.voice, dest)
        key = f"{verse['surah']}:{verse['ayah']}"
        manifest[key] = {
            "surah": verse["surah"],
            "ayah": verse["ayah"],
            "text": verse["text"],
            "src": f"ru/{verse['surah']}/{verse['ayah']}.mp3",
            "voice": args.voice,
            "provider": "Microsoft Edge TTS (edge-tts)",
        }
        print(f"[{index}/{total}] {key} {status} ({dest.stat().st_size:,} bytes)")
        await asyncio.sleep(args.delay)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nSaved manifest: {manifest_path}")
    print("These are test assets only; they have not been uploaded or connected to the live app.")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--surah", type=int, help="Generate one surah only (recommended for testing)")
    group.add_argument("--all", action="store_true", help="Generate every translation verse")
    parser.add_argument("--limit", type=int, default=0, help="Generate only the first N selected verses")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Edge TTS voice (default: {DEFAULT_VOICE})")
    parser.add_argument("--delay", type=float, default=0.15, help="Delay between requests in seconds")
    args = parser.parse_args()
    if not args.all and args.surah is None:
        parser.error("Choose --surah N for a safe test or --all to generate everything.")
    if args.surah is not None and not 1 <= args.surah <= 114:
        parser.error("--surah must be between 1 and 114")
    if args.limit < 0 or args.delay < 0:
        parser.error("--limit and --delay cannot be negative")
    return args


if __name__ == "__main__":
    try:
        asyncio.run(main_async(parse_args()))
    except KeyboardInterrupt:
        print("\nInterrupted. Existing MP3 files are retained; rerun to continue.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
