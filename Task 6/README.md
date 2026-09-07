# Task_06_Deep_Fake

## ⚠️ SYNTHETIC MEDIA DISCLOSURE

**Every audio/video artifact referenced in this repository is 100%
AI-generated.** No real person's voice or likeness is used without
their own consent. Voices and avatars used here are generic/stock
selections from ElevenLabs and HeyGen's libraries, not clones of any
real, identifiable, non-consenting person.

## Project description

This project transforms the Task 5 "coach" narrative — a
data-validated recommendation about the 2025 Syracuse Women's Lacrosse
season's fourth-quarter performance (see `script.md`) — into a
synthetic audio artifact, and produces a second, independent synthetic
video artifact from a self-written script on recent AI progress. Both
are critically evaluated, and the audio artifact has been run through
a detection check. The full write-up is in `EVALUATION_REPORT.md`.

## What's in this repo

| File | Purpose |
|---|---|
| `script.md` | The ~230-word narrative script (from Task 5's coach recommendation), edited for spoken delivery — used for Attempt 1 |
| `PROCESS_LOG.md` | Full attempt log: tools, versions, free-tier constraints, settings, and what went wrong on the way to what worked |
| `EVALUATION_REPORT.md` | Full critical evaluation of both artifacts, the detection check, and answers to the assignment's research questions |
| `EVALUATION.md` | Earlier working draft of the evaluation, in the assignment's original per-attempt template format |
| `DETECTION.md` | Template for a fuller detection/provenance check, if additional detection methods are run later |
| `artifacts/` | Where the synthetic files themselves belong — see "Outstanding items" below |

## Artifacts produced

1. **Audio (ElevenLabs, free tier)** — the full Task 5 coach narrative
   (`script.md`), synthesized with a generic stock voice matched to an
   analytical-coach register. To be saved as
   `artifacts/attempt1_elevenlabs_SYNTHETIC.mp3`.
2. **Video (HeyGen, free tier)** — a self-written ~150-word script
   about recent AI progress (different source material than the audio
   artifact — see `EVALUATION_REPORT.md` for why that limits a fully
   controlled comparison), rendered as a ~45-second avatar video after
   two stuck-at-97% render attempts. The free trial does not allow
   downloading the finished file, so this artifact currently exists
   only as a hosted link rather than a local file in this repo.

## How to reproduce this

1. Use `script.md` as-is for a voice-only artifact, or substitute your
   own Task 5 narrative (200-500 words).
2. **Audio:** create a free ElevenLabs account, choose a generic stock
   voice, paste in the script, and generate. Note your settings and
   any issues in `PROCESS_LOG.md`.
3. **Video:** create a free HeyGen account, choose a generic stock
   avatar, and generate from either your own script or a TTS file. If
   the render sticks at a fixed percentage, cancel and resubmit —
   HeyGen's own support documentation confirms this is a known,
   usually-temporary issue, and stuck/cancelled renders are not
   charged in credits.
4. Run at least one artifact through a detection check — asking a
   different LLM to evaluate the transcript/audio is a low-friction
   option; a public detector (Hive, Deepware Scanner) or a C2PA/
   watermark survival check are the more formal alternatives (see
   `DETECTION.md`).
5. Write up the evaluation using precise failure-mode language
   (prosody, breath, blink rate, cadence, watermark, temporal
   instability) rather than "sounds/looks fake" — see
   `EVALUATION_REPORT.md` for the completed example.

## Summary of what was learned

**Audio (ElevenLabs) held up better than video (HeyGen) on the free
tier.** The audio artifact is reasonably convincing to a casual
listener on first pass — voice selection and word-level emphasis are
both handled well — but fails on close listening due to a complete
absence of breath sounds and a flat emotional register that doesn't
track the shape of the argument. The video artifact does not hold up
at all: a visible watermark, unnatural avatar blink/cadence, and
low-effort b-roll editing make its synthetic origin immediately
obvious to anyone, regardless of familiarity with these tools.

**Effort to reach "convincing enough to fool a casual scroller" was
higher than expected**, and the main constraint was credits and
iteration limits rather than raw creative difficulty — free tiers on
both tools offered very few generation attempts, with more advanced
controls gated behind paid plans. Video generation alone took roughly
20 minutes of hands-on time to produce a result that was still
obviously synthetic; a more convincing result would likely require an
hour or two even with a paid tier removing the credit ceiling.

**Neither tool refused content in this project** — the restrictions
encountered were about iteration and export access (limited credits,
no free-tier video download, advanced features paywalled), not about
subject matter. Voice cloning specifically requires a consent step by
design, which was not tested directly here since no cloning was
attempted, but is a guardrail worth noting.

**Detection was straightforward for both artifacts, for different
reasons.** Asking a separate LLM to evaluate the audio correctly
identified it as synthetic, citing the monotonous rhythm, missing
breath sounds, and oddly-placed word emphasis. The video did not
require a formal detector at all — the watermark and avatar's
mechanical movement made its synthetic origin self-evident.

## Outstanding items before this repo is fully submission-ready

- Download the ElevenLabs audio file and add it to `artifacts/` as
  `attempt1_elevenlabs_SYNTHETIC.mp3`.
- The HeyGen video cannot currently be downloaded under the free
  trial's terms — either upgrade temporarily to export it, screen-record
  it with a clear disclosure overlay, or submit the hosted link
  alongside a note in this README explaining the access limitation (a
  hosted-link-only artifact is a real, documentable constraint, not
  something to hide).
- Confirm whether "Wizstar" or "HeyGen" is the correct tool credit for
  the video artifact — both names appear across this process, and the
  hosted link points to heygen.com.
- Consider whether to leave the audio/video scripts mismatched (Task 5
  narrative vs. self-written AI-progress script) or regenerate one to
  match the other for a cleaner controlled comparison — either choice
  is defensible, but the final README should state which was chosen
  and why.
