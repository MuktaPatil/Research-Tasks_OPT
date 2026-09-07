# Module 3 - Research Questions

Direct engagement with the assignment's research questions, drawing on
Modules 1 and 2.

---

**1. When you imagine the same technique deployed by someone whose
intentions you do not trust, what specifically becomes dangerous - the
technology itself, the delivery register, the scale of production, the
erosion of the audience's default assumptions, or something else?**

Based on the axis reasoning in Module 1, it's not the technology in
isolation - the exact same ElevenLabs pipeline used here is what a
bad-faith actor would use too, unmodified. It's the **combination** of
delivery register and audience assumption erosion working together.
The delivery register (a confident, measured "authority" voice) is
what makes a claim *feel* credible independent of whether it's true  - 
that's the mechanism identified in the Truth Axis. But that mechanism
is only dangerous at scale because audiences currently still extend a
baseline assumption that a voice speaking in that register represents
a real, accountable person. The erosion of *that specific assumption*
is the actual long-run danger - not that any one fabricated clip
fools someone, but that as fabrications become common knowledge, the
audience's default trust in *any* voice recording degrades, which
damages the evidentiary value of genuine recordings too. The technology
enables it; the delivery register is the specific lever; the erosion
of default trust is the actual harm, and it's a harm to the information
ecosystem generally, not just to any one deceived listener.

**2. Are the mitigations that would have caught your artifact the same
ones that would catch a bad-faith actor's? If a determined adversary
can defeat every mitigation on your list, no, and this is worth being
honest about rather than working around.**

Module 1's mitigation survey found that detection worked here mainly
*because* the artifact had residual tells (flat cadence, no breath
sounds, a visible watermark) that a more careful, better-resourced, or
simply next-generation effort would not necessarily have. The
mitigations that "caught" this project's artifacts were catching
*current-generation quality gaps*, not the *fact* of synthesis itself.
A determined adversary, especially one willing to pay for a
higher-quality tool tier or iterate more than a free-tier credit limit
allowed here, would face a meaningfully easier time evading exactly
these same detectors. This is a real asymmetry, not a solvable one:
mitigations built around *catching today's flaws* will structurally
lag behind a *generator specifically motivated to fix those flaws*, and
that gap doesn't close by trying harder at detection - it requires
mitigations that don't depend on the artifact being imperfect at all
(provenance/consent-at-source, for instance), which is exactly why the
Phase B policy in Module 2 leans on consent workflow and organizational
process rather than betting the whole policy on detection catching
violations after the fact.

**3. Where does your policy rely on people acting in good faith? Is
that reliance a fatal weakness, or is it inescapable in any policy that
governs human behavior?**

Addressed at length in `LIMITATIONS.md`. Short answer: nearly every
control in the Module 2 policy relies on good faith, and this is
inescapable rather than a design failure specific to this document  - 
any policy governing human conduct (not a technical access-control
system) ultimately depends on people choosing to comply. The honest
distinction isn't "does this policy rely on good faith" (all such
policies do) but "is the reliance appropriately scoped" - this policy
is explicit that its value is as a floor for good-faith actors and an
incident-response framework, not a technical guarantee against
adversarial misuse, which is the correct scope for a document like
this to claim.

**4. Is there a use of this technology you personally would refuse
regardless of what a policy permits? What is the source of that
refusal - a rule you can articulate, or something more like an
instinct?**

Yes: cloning a real, specific, identifiable person's voice or likeness
to make them appear to say something they did not say - regardless of
whether the statement itself is flattering, plausible, or something the
person might plausibly agree with if asked. This is articulable as a
rule (it's Section 2's first prohibited use in Module 2), not just an
instinct, and the rule traces directly back to the Consent Axis
reasoning: the harm isn't really about the content of the fabricated
statement at all, it's about removing a real person's control over
their own attributed speech. That holds even in a case with no
obviously bad content - a synthetic clip of a coach "saying" something
generically nice that she never actually said is still a violation of
the same principle, just with lower stakes. The rule generalizes better
than an instinct would, because an instinct calibrated only to "don't
make people say bad things" would miss this case entirely.

**5. Having done Task 6 and now this one, do you think the ethical
burden of synthetic media falls more on the person producing it, the
platform distributing it, the audience consuming it, or the regulator
overseeing it? Where would you locate accountability if you had the
authority to do so?**

Primarily on the producer, with real but secondary responsibility
distributed to platforms and regulators - and explicitly not on the
audience, whose role is to be appropriately skeptical but who cannot
reasonably be expected to detect synthesis that a purpose-built
detector might not even catch (per Module 1's detection-mitigation
findings). The producer bears primary responsibility because they are
the only party in the chain who has full knowledge of the artifact's
actual provenance at the moment of creation - everyone downstream
(platform, audience, regulator) is working with strictly less
information than the producer had. Module 2's policy reflects this
directly: nearly every control (consent workflow, approval gate,
provenance logging) sits at the point of production, because that's
the only point in the chain where complete information is actually
available to act on. Platforms bear real secondary responsibility for
building distribution systems that preserve rather than strip
disclosure and provenance signals (a genuine current failure, per
Module 1's Context Axis) - but even a perfect platform can't recover
information a producer never provided in the first place.

**6. Would you have written a materially different policy if you had
chosen a different organizational context? What does that tell you
about the portability of governance in this space?**

Almost certainly yes, and meaningfully so - a policy for, say, a
political campaign would need a much harder line on the Truth Axis
specifically (the persuasive/electoral stakes of a fabricated claim are
categorically different from an athletics department's), while a
K-12 school district's policy would likely center student-data and
minor-consent concerns barely relevant here. What's portable across
contexts is the *structure* - consent workflow, disclosure standard,
approval gate, incident response, and an explicit refusal section are
probably load-bearing in any serious policy regardless of setting.
What's *not* portable is which specific uses land in the "permitted"
vs. "prohibited" column, because that depends entirely on the
setting's own risk profile, audience, and institutional credibility at
stake. This suggests governance in this space is best built as a
**shared structural template with context-specific content**, not as
one universal policy - which is exactly why the assignment's
instruction to write for one specific, characterized setting (rather
than "everyone") produces a stronger, more honest document than a
generic one would.
