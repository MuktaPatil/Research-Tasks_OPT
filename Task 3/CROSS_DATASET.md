# CROSS_DATASET.md

## Which columns are shared?

27 of the `illuminating_*` scored columns (message type, topic, and
integrity/safety flags) appear in all three datasets with identical
names: Facebook Ads, Facebook Posts, and Twitter/X Posts. These are
0/1 flags produced by the same scoring process regardless of platform,
which makes them the one genuinely apples-to-apples comparison point
across otherwise very differently-shaped datasets (ads have spend and
targeting fields; posts have likes/shares/reactions; tweets have
retweets/quotes/views).

No other columns are shared verbatim — `page_id` (ads) / `Facebook_Id`
(posts) / no equivalent (tweets) all refer to a similar "who posted
this" concept but use different names, different value formats
(hashed page ID vs. hashed Facebook ID), and in Twitter's case, don't
exist as a column at all.

## Where the three platforms tell the same story

**Advocacy messaging is almost identical everywhere**: 54.9% of ads,
54.9% of Facebook posts, and 56.4% of tweets are flagged as advocacy
messages. Whatever "advocacy" captures in this scoring scheme, it's
apparently a near-universal baseline of political content regardless of
platform or whether the content was paid or organic.

**Most niche policy topics are rare and similarly rare everywhere.**
Flags like `lgbtq_issues_topic_illuminating`, `technology_and_privacy_
topic_illuminating`, `military_topic_illuminating`, and `education_
topic_illuminating` all sit under 2% on every platform, with almost no
spread between them. Niche-topic content appears to be a small,
consistent slice of political messaging no matter where it's posted.

## Where the three platforms tell different stories

**Calls to action are overwhelmingly an ads phenomenon.**
`cta_msg_type_illuminating` is set on **57.3%** of Facebook ads but only
**13.3%** of Facebook posts and **11.0%** of tweets — a >5x gap. This
makes intuitive sense: paid political ads exist specifically to drive
an action (donate, vote, RSVP), while organic posts are more often
simply communicating a message. The same pattern shows up even more
starkly in the CTA sub-types: `fundraising_cta_subtype_illuminating` is
22.8% on ads vs. under 2% on either posts platform, and
`voting_cta_subtype_illuminating` is 14.4% on ads vs. under 2.5%
elsewhere. If you only had the organic post data, you'd badly
underestimate how much of this election's messaging was built around
explicit calls to action — because virtually all of that activity ran
through paid ads specifically.

**Issue-based messaging is highest on Twitter, not lowest.** This one
runs the opposite direction from what "ads are the persuasion channel"
intuition would predict: `issue_msg_type_illuminating` is 50.8% on
Twitter, 46.0% on Facebook posts, and only 38.2% on ads. Attack-style
messaging (`attack_msg_type_illuminating`) is also slightly higher on
Twitter (30.8%) than on ads (27.2%) or Facebook posts (21.7%). Twitter
content in this dataset skews more toward substantive/issue and
attack-oriented framing relative to the other two platforms, rather
than the straightforward "ads are the aggressive channel" story you
might expect going in.

**Health and women's-issue topics show up more in paid ads than organic
content.** `health_topic_illuminating` is 10.9% on ads vs. 4.9-5.6%
elsewhere; `womens_issue_topic_illuminating` is 8.1% on ads vs.
2.3-2.5% elsewhere. Advertisers appear to be targeting these topics
more deliberately than organic posters raise them on their own.

**Scam and integrity flags are also concentrated in ads.**
`scam_illuminating` is 7.2% on ads vs. 1.2-2.0% on posts/tweets. Whether
this reflects genuinely more scam-adjacent content in paid political
advertising, or simply that the scoring model was tuned more
specifically for ad copy, isn't something this dataset alone can
answer — it's worth flagging as a question for whoever built the
scoring pipeline rather than treating as settled fact.

## What might explain these differences

The most parsimonious explanation for most of the ad-vs-organic gaps is
purpose: ads are bought specifically to convert (donate, vote,
volunteer), so CTA-heavy and topic-targeted framing is a structural
feature of the format, not a campaign-specific choice. The Twitter
exception (higher issue/attack rates than ads) suggests organic
political discourse on that platform in this window skewed more
combative/substantive than either platform's paid advertising — which
is also consistent with Twitter/X posts in this dataset being a curated
set from a smaller number of highly active political accounts, whose
posting style may not generalize to "how political content looks on
Twitter" broadly.
