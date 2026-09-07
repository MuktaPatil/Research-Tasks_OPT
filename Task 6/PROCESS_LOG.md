# PROCESS_LOG.md

Running log of every attempt made in this project, in chronological
order.

---

## Attempt 0 — Local open-source pipeline (bonus challenge attempt)

**Tool attempted:** An offline/local TTS engine (espeak-ng, festival,
flite, pyttsx3, or Coqui TTS), explored as a possible no-cost,
no-account alternative before moving to web-based tools.

**Environment:** A sandboxed development environment with no outbound
network access — confirmed by checking for existing TTS binaries
(`espeak`, `festival`, `flite`, none found as runnable executables)
and attempting to import TTS-related Python packages (`pyttsx3` not
installed, and not installable without network access).

**Result:** No usable local TTS pipeline was available, and none could
be installed in this environment.

**Time spent:** ~10 minutes.

**Finding:** This is a useful data point on its own, directly relevant
to the assignment's bonus prompt about "what the polished consumer
tools are hiding from you." Web tools like ElevenLabs make voice
synthesis feel like a one-click solved problem. Underneath that is
normally a real dependency stack — model weights (often several GB),
a working audio backend, and often a GPU — that a locked-down or
offline environment simply doesn't have by default. Anyone wanting to
pursue this bonus challenge for real should do it on a personal
machine or a hosted notebook environment with network and GPU access
(e.g. Google Colab), not a fully offline sandbox.

---

## Attempt 1 — ElevenLabs (audio only)

**Tool + version:** ElevenLabs, free tier, web app.

**Free-tier constraints in effect:** limited monthly character
allowance, restricted voice library, no paid-tier fine-tuning
controls, and no meaningful redo/iteration allowance beyond the
included generations.

**Voice used:** a generic stock voice from ElevenLabs' library,
selected to match the register of an analytical coach. Per the
assignment's constraint, this is not a clone of any real, identifiable
person's voice. A brief check of how ElevenLabs' voice library is
built also confirmed that available voices are sourced from
consenting voice actors, and that cloning an arbitrary person's voice
requires a consent step the free tier does not bypass.

**Script used:** the full text of `script.md` — the Task 5 coach
narrative on the Syracuse women's lacrosse season's fourth-quarter
performance.

**What went wrong on the way to what went right:** minimal friction —
this was a clean result on the first generation, with no re-rendering
required. The limitations that surfaced were in the *output itself*
(see `EVALUATION_REPORT.md`: no breath sounds, flat emotional range)
rather than in getting the tool to function.

**Output:** audio narration of the Task 5 coach narrative. To be saved
as `artifacts/attempt1_elevenlabs_SYNTHETIC.mp3`.

**Time spent:** low — a single generation, no iteration cycles needed
to reach a usable result.

---

## Attempt 2 — HeyGen (video, free tier)

**Tool + version:** HeyGen, free tier, web app. (Note: an earlier tool
referred to as "Wizstar" was attempted first and did not produce a
usable result; the working output is hosted on heygen.com. Confirm the
correct tool name before final submission — this log currently credits
both, pending that confirmation.)

**Free-tier constraints in effect:** watermarked output; **no option
to download the finished file** on the free trial, meaning the
artifact currently exists only as a hosted link rather than a portable
file; very limited number of generation credits, with no meaningful
redo allowance once those credits were used; more advanced controls
(e.g. "director mode"-style scene direction) gated entirely behind a
paid tier.

**Script used:** a self-written ~150-word script on recent
improvements in AI — different source material than Attempt 1's Task
5 narrative. This means Attempts 1 and 2 are not a fully controlled
"same content, different tool" comparison; that tradeoff is
acknowledged rather than hidden.

**What went wrong on the way to what went right — the render got
stuck at 97% completion, twice:**
1. First render attempt: stuck at 97% indefinitely.
2. Diagnosed against HeyGen's own documented common causes (queue
   concurrency, account/credit standing) — neither seemed to apply
   directly, so the render was cancelled and resubmitted per HeyGen's
   own recommended fix.
3. Second render attempt: also stuck at 97%.
4. A working render was eventually produced, but the free tier's
   inability to export a downloadable file remained in effect
   regardless of the render issue being resolved.

**Output:** a roughly 45-second avatar video, narrating the AI-progress
script. Currently available only via its hosted link (see
`EVALUATION_REPORT.md`); could not be downloaded into this repository
under the free trial's terms.

**Time spent:** substantially more than Attempt 1 — roughly 20 minutes
of hands-on generation time alone, not counting the two stuck-render
cycles and the diagnostic steps taken in response. This gap between
the audio and video pipelines' time cost is itself a finding worth
carrying into the README: video pipelines cost meaningfully more
troubleshooting time than audio-only pipelines, even before evaluating
the quality of the result.

---

## Attempt summary table

| Attempt | Tool | Modality | Time spent | Usable output? |
|---|---|---|---|---|
| 0 | Local (espeak/flite/Coqui) | Audio | ~10 min | Blocked — no network access to install/run |
| 1 | ElevenLabs | Audio | Low — one clean generation | Yes — see EVALUATION_REPORT.md for quality notes |
| 2 | HeyGen | Video | High — ~20 min generation + 2 stuck-at-97% render cycles | Yes, but watermarked and not downloadable on the free trial |

---

## What triggered restrictions, refusals, or degraded output

Neither tool refused content outright in this project — the script
material (sports analysis; general commentary on AI progress) did not
trigger any content-based blocks. The restrictions encountered were
entirely about **iteration and access**, not content:
- Both free tiers offered a limited number of credits/generations with
  no meaningful way to redo or refine a result once spent.
- HeyGen's free trial does not permit downloading the finished video
  at all — a hard access restriction independent of content.
- More advanced creative controls (scene/director-level direction)
  were gated behind paid tiers on more than one tool explored during
  this project.
- Voice cloning specifically requires a consent step by design
  (confirmed via ElevenLabs' own documentation on how its voice
  library is sourced) — this project did not attempt to clone a real
  person's voice, so this was not tested directly as a refusal, but is
  noted as a built-in guardrail rather than something either tool
  glosses over.
