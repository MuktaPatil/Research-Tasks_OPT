# FINDINGS.md

## What's in the data

The dataset holds 246,745 Facebook/Instagram ad purchases from the 2024
U.S. presidential race, each one placed by an organization whose ad
mentioned at least one presidential candidate. It runs from late
September through early November 2024 — essentially the final stretch
of the campaign — and covers 4,546 distinct advertiser pages, from major
campaign committees down to small PACs and partisan pages most people
have never heard of.

## Spending is concentrated in a small number of hands

Total estimated spend in the dataset is roughly **$262 million** (using
the midpoint of Meta's reported spend ranges — see the README for why
that's an approximation, not an exact figure). Despite 4,546 distinct
pages placing ads, spending is far from evenly distributed: the **top 10
spenders account for about 63% of all spend**. Kamala Harris's own
campaign page alone is responsible for roughly a third of total spend in
the dataset ($82.8M), more than three times what Joe Biden's page spent
($26.4M) and more than four times Donald J. Trump's official page
($19.6M). Down the list, official party infrastructure (Kamala HQ,
Biden-Harris HQ, Senate Democrats), major outside-spending groups
(Future Forward, America PAC, AFP Action), and at least one page whose
name gives no obvious indication of its politics (The Daily Scroll, at
$6.1M) round out the top spenders.

This concentration is a familiar pattern in campaign finance research:
a handful of well-funded committees dominate the paid-media landscape,
while a long tail of thousands of smaller pages each spend comparatively
little. It's worth noting that Trump's own committee page is not the
single biggest spender in this dataset — that doesn't mean the
Trump campaign spent less overall, only that a larger share of
pro-Harris ad spend seems to have run through the campaign's own page
rather than through affiliated PACs, at least among the accounts
captured here.

## Spending has a clear, sharp shape over time

Daily spend climbs unevenly through October — with visible bumps around
early October and mid-October — before spiking hard in the final days of
the campaign: **October 27th and 28th are the two highest-spending days
in the entire dataset**, with October 28th alone accounting for over
$11.3 million in estimated spend, roughly double any other single day.

Then spend collapses almost to zero starting October 29th and stays
there through Election Day (November 5th). This isn't noise — it lines
up with Meta's well-documented policy of blocking *new* political ads
during the week immediately before a U.S. election, while still
allowing previously-approved ads to keep delivering at reduced volume.
The dataset's shape is a direct fingerprint of that platform policy, not
a sign that campaigns simply stopped wanting to advertise right before
the vote.

## Trump is mentioned more than anyone — including by his opponents

Looking at the `illuminating_mentions` field (which candidates an ad's
text actually names, regardless of who paid for it), Donald Trump is
the single most-mentioned candidate in the dataset at 78,324 mentions,
well ahead of Kamala Harris (53,239). Joe Biden and "President Biden"
combined still show up over 40,000 times, reflecting the period before
he dropped out of the race in this same window. JD Vance appears about
12,000 times and Tim Walz about 8,500 — each considerably less than
their running mates, which fits the intuition that vice-presidential
picks generally draw less direct ad-copy attention than the top of the
ticket.

The fact that Trump is mentioned more often than Harris, even though
Harris-aligned pages spent more money overall, suggests a lot of that
Harris-side spending went into *attack* ads that name Trump rather than
purely promotional ads about Harris herself. That's consistent with the
`illuminating_msg_type_attack` flag being set on about 27% of all ads in
the dataset — a substantial share of this advertising isn't about
promoting a candidate at all, it's about opposing one.

## What surprised me

Two things stood out. First, how binary the platform-policy effect on
timing is — I expected spend to taper off before the election, not
essentially hit zero overnight on a specific date. Second, how much of
the "spend" and "audience size" data isn't actually numeric in the raw
file — it's a privacy-preserving range object, which meant a meaningful
chunk of the real analytical work here was deciding how to turn ranges
into numbers before any statistics could be computed at all, rather than
computing statistics per se.
