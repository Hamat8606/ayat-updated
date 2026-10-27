# Russian translation audio experiment

This branch is deliberately isolated from `main`. It does not change the live app or the existing recognition, highlighting, or Arabic recitation.

## Goal

Prepare MP3 files from the Russian translation already embedded in `index.html`, one file per ayah. The phone will then play an ordinary audio file instead of calling `speechSynthesis` for the Russian translation. The same HTML audio playback path can be used on iPhone Safari and Android Chrome; actual automatic transitions still need testing on both devices.

## First test only

1. Install Python 3.10+.
2. Install the generator dependency: `python -m pip install edge-tts`.
3. Run `python tools/generate_ru_audio.py --surah 1`.
4. Listen to the resulting files under `generated-audio/ru/1/` and compare each recording with its matching translation in the app.
5. Do not run `--all` until voice quality, pronunciation, text matching, generation reliability, and total storage requirements have been assessed.

The script reads the translation directly from the current HTML data block, writes one MP3 per verse, and creates a JSON manifest. It is resumable: existing nontrivial MP3 files are skipped. It does not edit the app or upload audio.

## Important limitations

- `edge-tts` uses an online Microsoft Edge text-to-speech service; it is not a local/offline generator and its availability or terms may change. This is an experiment, not a production commitment.
- The voice is synthetic, but playback on the phone is prerecorded MP3, not live browser speech synthesis.
- Generated audio must not be committed to the app repository or deployed to GitHub Pages before estimating the full size. GitHub recommends keeping large generated assets outside the Git repository. Choose an audio host only after the sample test and licensing/terms review.
- HTML audio playback is broadly supported on iOS and Android, but browsers can restrict programmatic playback. Test the entire sequence on both platforms, including the initial user gesture, playback end event, and return to Arabic speech recognition.
- The existing main branch remains the rollback point. Do not merge this experiment into `main` until the sample works on both iPhone and Android.
