**Synthetically Generated Artifacts: Evaluation Report**

**A. Artifact Details**

**Artifact 1 --- Audio (ElevenLabs).** A voice-synthesized reading of the Task 5 coach narrative (script.md), analyzing the Syracuse women's lacrosse team's fourth-quarter performance and identifying a player to build a game plan around. Generated on ElevenLabs' free tier using a generic stock voice --- no real person's voice was cloned.

**Artifact 2 --- Video (HeyGen).** A ~45-**second** avatar video (free tier), narrating a self-written script on recent improvements in AI. The free trial does not permit downloading the finished file, so this artifact is currently available only via its hosted link rather than as a local file in this repository. see the note in Section C on why that limits how thoroughly it could be evaluated.

**Video:** [Video Link](https://app.heygen.com/videos/ai-reflections-the-new-frontier-bfdad04883304f97be8f8975a795dbe6)

**B. Model Evaluation**

**1. Audio (ElevenLabs)**

**Where does it hold up? What would a casual viewer accept without question?**

The voice selection is genuinely well-matched to the character: it reads as a measured, analytical coach walking through game film, not a generic narrator reciting statistics. The model also handles emphasis competently --- it stresses the correct words in number-heavy sentences rather than flattening them into a monotone list. A casual listener would very likely accept this clip at face value on a first pass; they might sense that *something* feels slightly composed or "off," but nothing here is an obvious tell that would make them stop and think "this is AI."

**Where does it fail?**

The clearest failure is the complete absence of breath sounds. A real speaker inhales audibly between clauses, especially when making a point they care about --- this output has none of that, which reads as subtly "too smooth" under close listening even though it never sounds robotic in the classic sense. Beyond that, the delivery is missing *emotional range*: the model correctly identifies which syllables to stress, but the overall energy stays nearly constant from start to finish. A real coach delivering this argument would likely get more animated on the recommendation ("this is who I'd build around") and flatter on the setup --- this output doesn't vary its intensity to match the shape of the argument. Some of this is attributable to the script itself, which was written for clarity rather than performed delivery, and some to the constraints of a free-tier product with no fine-tuning of delivery style. Overall, it is well-made within those limits, but the limits are real.

**Would you be fooled by this if you did not know it was synthetic? Would someone outside the field?**

Not entirely. The pacing occasionally reads as abrupt, and the flat emotional register is the kind of thing that becomes more noticeable the longer you listen - the clip is missing the punctuation of excitement or concern that a real coach would bring to sentences about their own team's weaknesses and strengths. Someone outside this field might not name the issue precisely, but would likely still sense that the delivery feels slightly rehearsed or composed rather than spontaneous.

**2. Video (HeyGen)**

**Where does it hold up? What would a casual viewer accept without question?**

Very little holds up here, and that is a legitimate finding rather than a shortcoming to minimize. Because this was generated on the free tier, the output is watermarked throughout, which alone removes any ambiguity about its synthetic origin before evaluating anything else. Beyond the watermark, the avatar's blinking pattern and speech cadence both read as noticeably artificial rather than natural. This would not pass as authentic to a casual viewer.

**Where does it fail? (Prosody, breathing, blinking, lip-sync, hands, background stability, emotional register, cadence)**

-   **Watermark:** an immediate, unmissable synthetic-media indicator, present across the entire clip.

-   **Blink rate / eye behavior:** the avatar's blinking does not track naturally. It reads as irregular in a way that draws attention rather than disappearing into the performance.

-   **Cadence:** the avatar's speech rhythm does not convincingly match natural human speaking patterns; combined with the script itself (self-written, and not optimized for spoken delivery), the overall effect feels mechanical rather than conversational.

-   **B-roll / supporting visuals:** the surrounding clips used to illustrate the narration feel disconnected and low-effort -"clanky" transitions that further undercut any illusion of a produced, intentional piece.

**Would you be fooled by this if you did not know it was synthetic? Would someone outside the field?**

No, not at all, and this holds regardless of familiarity with synthetic media. The watermark alone would tip off any viewer, expert or casual, before questions of avatar realism or cadence even become relevant.

**C. Detection / Provenance Check**

The audio artifact was submitted to Claude for evaluation of whether it read as AI-generated. Claude correctly identified it as synthetic.

The video artifact could not be submitted for the same kind of check, because the free-trial tier does not permit downloading the finished file . Thus, the evaluation was limited to what is visible through the hosted link itself. That said, no formal detector was actually needed here: the video's synthetic origin is self-evident on inspection, through the visible watermark and the avatar's noticeably mechanical movement. **This asymmetry is itself worth noting as a finding**: a detection tool's job is easy when the artifact is low-quality enough to be visually self-incriminating, and the free tier's own limitations (the inability to export a clean file) end up serving as an accidental provenance safeguard, whether or not that was the platform's intent.

**D. Research Questions**

**1. Which failures were most noticeable to you as the creator, and which do you think would be most noticeable to someone who has never used these tools? Are they the same?**

Largely, yes, though for different reasons. For the audio, the flat emotional register was the most noticeable issue from a creator's perspective. But a first-time listener likely wouldn't name that specific quality; they would more likely just describe the clip as "fine, but a little stiff," without being able to say why. For the video, the gap between creator and casual-viewer perception mostly disappears: the watermark is impossible to miss regardless of how familiar someone is with synthetic media, so everyone converges on the same immediate conclusion.

**2. Where did the tools refuse or degrade? Did any refuse to clone a voice without proof of consent? Did any refuse political content? What patterns did you notice in what got blocked and what got through?**

The free-trial tiers used here were restrictive primarily around *iteration*, not content. Neither tool offered redo attempts within the free trial's constraints, which meant limited room for prompt-engineering or refining a result once generated. On the consent question specifically: the voices available were sourced from consenting voice actors rather than cloned from arbitrary audio, and the platform's own documentation supports this - a brief check of how the voice library is built confirms the model would not permit cloning an arbitrary person's voice without a consent step. Several tools also gated more advanced iteration or scene-direction features (e.g. "director mode"-style controls) behind a paid tier entirely, meaning the free experience is deliberately narrow both in creative control and in number of attempts.

**3. How much effort did it take to get to "convincing enough to fool a casual scroller"? Was that effort measured in hours, in tool credits, or in prompt-engineering iterations?**

More effort than expected, and the constraint was mostly credits and iteration limits rather than raw time. On the free trial, a limited credit allotment meant very few opportunities to refine a result before running out of attempts; some tools offered no meaningful iteration at all without upgrading to a paid tier. In terms of hands-on time, the video generation process alone took roughly 20 minutes to produce a result that was obviously synthetic rather than convincing. Even accounting for a hypothetical paid tier removing the credit ceiling, a realistic estimate for reaching something that could plausibly fool a casual scroller would be on the order of one to two hours of iteration and even then, audiences have become more attuned to AI-generated content over the past couple of years, so even a small remaining tell (an odd cadence, a slightly wrong blink pattern) is often enough to give it away to anyone paying moderate attention.

**4. What did the detection tools actually catch? Did they explain themselves, or did they hand you a confidence score with no reasoning?**

For the audio, the tell-tale signs were the near-monotonous rhythm across sentences, the complete absence of breathing sounds, and oddly-placed emphasis on certain words that a human speaker would not naturally stress. These were explained qualitatively rather than returned as a bare confidence score- the reasoning was legible and specific, not just a number. For the video, the giveaways were even more immediate: the avatar's static, slightly unnatural positioning, low-quality and disconnected b-roll footage, and --- most decisively --- the visible watermark, which made any deeper analysis almost unnecessary.

**5. Would your evaluation of this technology change if the subject were a real named person rather than a synthetic voice or generic likeness?**

Most likely, yes. The stakes and scrutiny would both increase substantially. That said, it's worth noting that the underlying tells identified here are not really about *whose* likeness is being used; they are about the production quality of the artifact itself. The script read as AI-generated for both the voice and video versions regardless of whose voice or face was attached to it, and the supporting details such as vocal intonation patterns for the audio, and low-effort b-roll editing for the video, would still give away the synthetic origin even if the underlying likeness belonged to a real, recognizable person. In other words, swapping in a real identity would raise the ethical and reputational consequences of a convincing forgery considerably, but it would not, on its own, fix the specific technical weaknesses that made these particular artifacts identifiable as synthetic.
