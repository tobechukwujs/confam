# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Delegated. The builder and their stack are not confirmed yet, so the design ships as a framework-free HTML/CSS/JS prototype plus a written spec that can move into any setup. The verification engine is Python.

## Users

- **Primary: a Nigerian voter on WhatsApp.** They have just received a forwarded "official" election notice, in a family, church, market or work group. They want to know if it is real before they act on it or pass it on. They are often on a budget Android phone with limited data, sometimes outdoors in strong light, and may be more comfortable in Pidgin, Hausa, Yoruba or Igbo than in English. Some are low-literacy and some have disabilities.
- **Secondary: someone without WhatsApp access, or someone who followed a Confam link.** They use the public web checker, or open a verdict page to check that a Confam reply is genuine.
- **Operator: a Confam reviewer.** They approve new official notices before the verifier can use them. Every entry needs two people. They need to see exactly what changed and be sure nothing is added by accident.
- **Evaluator: hackathon judges and mentors.** They see a three-minute video and a live demo on 15–16 December 2026.

## Product Purpose

Confam turns "verify through official channels" into a few seconds' work, inside the app where fakes actually spread. A person forwards a notice. Confam compares it with the official record and replies in their language with what is true, what changed and where the original is.

Success is a person who was about to act on, or forward, a false notice and did not, and a person with a genuine notice who trusts it.

## Positioning

"Don't detect the fake, confirm the real." Confam never guesses whether something looks fake. It lays the forwarded copy against the authority's own published record and shows the exact detail that differs. Fact-check tiplines wait for a human to write a debunk. AI detectors guess. Image fingerprints miss a one-digit date change. Confam shows the receipt.

## Operating Context

- **Primary channel:** WhatsApp Business. The chat interface cannot be styled, so design lives in the wording, the order of messages and the verdict image the bot sends. Telegram and web are fallbacks.
- **Verdicts the user sees:** CONFIRMED, ALTERED, NOT OFFICIAL. Two more honest outcomes exist: PARTIAL (the crop is missing part of the notice) and CANNOT CONFIRM (the engine is unsure, or the notice is not in the record yet).
- **"Not in our record" never means "fake".**
- **Speed:** about 9 seconds per check on a laptop CPU today, so the wait must be designed.
- **Reply layer:** fixed templates reviewed by native speakers. Official text is quoted word for word. No AI-written facts reach a user.
- **Watch loop (from the Ìbò pitch):** Confam watches public official sources and drafts a record entry with a diff. A person approves it before it can be used.
- **Voice notes (from the Ìbò pitch):** a user can send a voice note. Confam reads back what it understood, then checks it. Voice replies are available for low-literacy users.
- **Cost:** WhatsApp is reported to charge about ₦14 per business reply from October 2026, so replies stay short and few.

## Capabilities and Constraints

- Tracks: Track 1 (problem 1C, provenance for official communications) with a Track 4 anti-phishing element.
- Five languages: English, Nigerian Pidgin, Hausa, Yoruba, Igbo. The product must render Hausa ɓ ɗ ƙ, Yoruba ẹ ọ ṣ with tone marks, and Igbo ị ọ ụ ṅ correctly.
- Confam replies in the language the sender used.
- Every reply links to a public verification page, so a forged screenshot of a Confam reply proves nothing.
- Hard red lines: nonpartisan; never touches BVAS, IReV or the voter register; synthetic, public or authorised data only; human oversight; winning does not mean deployment.
- Privacy: no images kept after the check, phone numbers hashed, short retention.
- Engine limits today: tested on clean typed notices from a fictional commission only. Real letterheads, stamps and signatures are untested. Rumours with no checkable fact are not handled.
- Undecided: the final name (trademark unchecked), the public domain and the WhatsApp number.

## Brand Commitments

- Name: "Confam" (working name; Nigerian slang for "is it confirmed?").
- Voice: match the sender's language. Calm and plain. Never jokes about a fake, never shames the person who forwarded it.
- Confam must never look like INEC or any government body. It is an independent checker and must not impersonate the authority it checks.
- Confam must not resemble any political party's colours or symbols.

## Evidence on Hand

- `Confam_Idea_Brief.pdf`: the problem, sources, tests, rubric fit, plan.
- `#AI4Elections Pitch — Ìbò.pptx`: source of the watch loop, voice notes and the "Autonomy with a ceiling" framing.
- `flyer.jpeg`: the official hackathon flyer.
- Test results: 15 of 15 hand-built cases correct; in 165 cases, 98 of them fakes, no fake was confirmed as genuine. In the 150-case run, 7 of 60 honest copies were false alarms. A fix exists but its full rerun has not finished, so no improved figure may be quoted.
- Fixture content: the fictional "Simulated Electoral Commission" notices used in testing.
- Absent, and not to be invented: users, testimonials, partners, endorsements, deployment, real INEC approval, or any real-world accuracy figure.

## Product Principles

1. Show the receipt. Every verdict carries the official words, the source and the exact change. Trust comes from being able to see it.
2. Honest before confident. "Cannot confirm" is a real answer, and "not in our record" is never "fake".
3. The person is not the problem. Forwarding a fake is a mistake to help with, never a failure to shame.
4. Humans hold the record. No notice enters it, and no broadcast leaves, without human approval.
5. Built for the group chat. A verdict must make sense on a cheap phone, in strong light, after being forwarded again.

## Accessibility & Inclusion

- WCAG 2.2 AA minimum across the web surfaces, and readable outdoors on budget Android screens.
- A verdict is never carried by colour alone: the word and the shape must also carry it.
- Low-data by default: the web checker must work on a slow 3G connection.
- Voice input with read-back and voice replies for people who read with difficulty.
- All five languages are first-class, including in the verdict image.
- Hausa, Yoruba, Igbo and Pidgin strings in the prototype are drafts until a native speaker has reviewed them.
