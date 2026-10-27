# Russian audio experiment — test scope

The isolated GitHub Actions workflow `.github/workflows/generate-fatiha-audio.yml` is intended to:

1. Download the first Russian Quran translation MP3 attachment from the IslamHouse source page.
2. Generate seven test MP3 files from the app's embedded translation using Edge TTS.
3. Check that all seven generated files and manifest entries exist and are non-empty.
4. Bundle the source recording, generated files, and a local HTML listening page as a temporary Actions artifact.

This does not publish audio to GitHub Pages or modify the protected original repository. A successful workflow run checks download and file integrity only; a human still needs to listen to the source and generated files and compare their wording and verse boundaries.
