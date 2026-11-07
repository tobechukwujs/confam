---
name: Confam
description: Marks a forwarded election notice against the official record, the way a teacher marks a script.
colors:
  biro-blue: "#1b2e96"
  cover-deep: "#14226f"
  cover-line: "#5766c2"
  cover-text: "#e9ecfb"
  red-biro: "#c40d23"
  green-biro: "#0a6b42"
  pencil: "#555b65"
  print-black: "#14171c"
  soft-print: "#4a525e"
  page: "#f6f9fb"
  sheet-white: "#ffffff"
  feint-rule: "#d3deea"
  page-edge: "#a9bcd2"
  wash: "#e6edf4"
  selected-tint: "#dfe5f6"
typography:
  display:
    fontFamily: "Andika, Roboto, Noto Sans, Segoe UI, system-ui, sans-serif"
    fontSize: "52px"
    fontWeight: 700
    lineHeight: "60px"
    letterSpacing: "-0.015em"
  display-phone:
    fontFamily: "Andika, Roboto, Noto Sans, Segoe UI, system-ui, sans-serif"
    fontSize: "40px"
    fontWeight: 700
    lineHeight: "60px"
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Andika, Roboto, Noto Sans, Segoe UI, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: "30px"
  body:
    fontFamily: "Andika, Roboto, Noto Sans, Segoe UI, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: "30px"
  label:
    fontFamily: "Andika, Roboto, Noto Sans, Segoe UI, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: "30px"
  hand:
    fontFamily: "Playwrite NG Modern, Segoe Print, cursive"
    fontSize: "42px"
    fontWeight: 400
    lineHeight: "90px"
  notice:
    fontFamily: "Arial, Liberation Sans, Helvetica, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: "24px"
rounded:
  sm: "3px"
spacing:
  line: "30px"
  double-line: "60px"
  gutter-phone: "14px"
  margin-phone: "38px"
  gutter-wide: "40px"
  margin-wide: "60px"
components:
  button-primary:
    backgroundColor: "{colors.biro-blue}"
    textColor: "{colors.sheet-white}"
    rounded: "{rounded.sm}"
    height: "60px"
  button-primary-hover:
    backgroundColor: "{colors.cover-deep}"
  button-line:
    backgroundColor: "transparent"
    textColor: "{colors.biro-blue}"
    rounded: "{rounded.sm}"
    height: "60px"
  field:
    backgroundColor: "transparent"
    textColor: "{colors.biro-blue}"
    rounded: "0px"
  switch-selected:
    backgroundColor: "{colors.selected-tint}"
    textColor: "{colors.biro-blue}"
    rounded: "{rounded.sm}"
    height: "60px"
---

# Design System: Confam

## Overview

**Creative North Star: "The Marked Script"**

Every Nigerian who went to school knows how to read a marked script: a tick means right, a red ring means look here, and the correction sits beside it. Confam uses that literacy instead of teaching a new one. The surface is a flat open exercise book lying on a biro-blue cover. The page stays quiet so that the only loud thing on any screen is the mark.

The notice is what gets marked, never the person. There are no scores, no grades and no school jokes. Confam has no shields, scanners, confidence percentages or status pills.

The book is flat. There is no paper grain, no embossing and no curl. Physicality comes from behaviour: text sits on the rules, marks are drawn by a pen, and two staples hold the spread.

**Key Characteristics:**
- One ruled line (30px) sets every vertical measure.
- Colour lives only in the marks, the cover and the primary action.
- Marks are pen strokes generated to fit what they mark, so no two match.
- The verdict fits one budget phone screen.
- All five languages render at full weight, including Hausa hooked letters and Yorùbá tone marks.

## Colors

A committed biro-blue cover holds a restrained page, with three pens used only as marks.

### Primary
- **Biro Blue:** the cover, the primary action, links, and anything the person writes.

### Secondary
- **Red Biro:** only where a copy differs from the official record.
- **Green Biro:** only for a match with the official record.
- **Pencil:** only when Confam is unsure.

### Neutral
- **Print Black:** all text on the page.
- **Soft Print:** secondary text, kept above 4.5:1 on the page.
- **Page:** the cool white of the exercise book.
- **Sheet White:** the forwarded notice lying on the page.
- **Feint Rule and Page Edge:** ruled lines, margin line, table lines.

### Named Rules
**The Quarantine Rule.** Red appears only where a copy differs from the record. Form errors, warnings and decoration are never red. If a screen has nothing wrong with the notice, it has no red on it.

**The Three Pens Rule.** The pen carries the certainty: green for a match, red for a difference, pencil for not sure. Shape and word carry it too, so nothing depends on colour alone.

**The Not INEC Rule.** The palette never borrows from the electoral body or a political party. Blue is the brand, and green stays a mark.

## Typography

**Body and Display:** Andika, a typeface designed for literacy, with single-storey a and g and full coverage of Nigerian orthographies.
**Hand:** Playwrite NG Modern, drawn from Nigerian primary-school handwriting.
**Notice:** Arial, so the document reads as someone else's print.

**Character:** Andika is the calm voice of the page. The hand is Confam's pen, and it appears only for corrections.

### Hierarchy
- **Display:** verdict words and page questions.
- **Headline:** section headings on the page.
- **Body:** everything a person reads, at a generous 18/30 for low-literacy and outdoor reading.
- **Label:** metadata and notes.
- **Hand:** the corrected figure, and signatures on the desk.
- **Notice:** the forwarded document only.

### Named Rules
**The On-The-Line Rule.** Text sits on the rules like handwriting. Baseline is line-height/2 + 0.4em, and the rules are set to fall 3px under the 18/30 baseline. Each larger size carries its own small nudge.

**The Quoted Word Rule.** Hand corrections and official quotes stay in the notice's own language, word for word. Interface words change language; the record does not.

**The Hand Is For Corrections Rule.** Playwrite covers Basic Latin only, so it never sets interface copy.

## Layout

Below 900px there is one page. Its left margin (38px) holds marks and numbered pins, with a 14px right gutter. From 900px the book opens into a two-page spread up to 1280px wide: the left page is the answer and the right page is the proof. Two staples mark the fold.

All vertical spacing is a multiple of the 30px line. Controls are 60px tall, two lines.

The marking desk is the dense exception. It uses a 24px rhythm and three panes from 1000px: queue, notice, sign-off.

### Named Rules
**The One Screen Rule.** At 360 by 640, the verdict word, the marked figure, the sentence, the instruction and the main action all fit without scrolling.

**The Scale Rule.** The changed figure is the largest thing on the screen. Scale alone ranks it.

## Elevation & Depth

The system is flat. The only raised object is the forwarded notice, which lies on the page.

### Shadow Vocabulary
- **Lying on the page:** a small close shadow plus a soft low shadow, on notice sheets only.
- **Chat frame:** the same idea, larger, on the WhatsApp simulation only.

## Shapes

Square corners throughout. Buttons take a slight 3px softening and text fields none. Rounded forms appear only inside the WhatsApp simulation, because that is WhatsApp's shape, not ours. Numbered pins are circles because they are ring marks.

## Components

### Buttons
- **Primary:** Biro Blue, white bold text, 60px tall, full width on a page.
- **Line:** a 2px Biro Blue outline for secondary actions.
- **Hover / Focus:** hover deepens the blue. Focus is a 3px outline with a 2px gap. Press moves 1px down.
- **Disabled:** Wash fill with Soft Print text.

### Inputs / Fields
- **Style:** transparent over the rules with a 2px Biro Blue edge. Typed text is Biro Blue and sits on the lines.
- **Focus:** the edge thickens to 3px.
- **Error:** the edge turns Print Black and a bold message appears below. Errors are never red.

### Navigation
- **Style:** white text on the cover. On wide screens, all five languages are visible. On phones, the current language opens a row of all five.

### The Mark
The signature component. Each difference type has one mark.
- **Replace:** a red ring with the official value handwritten above it.
- **Insert:** a red strike through the added words.
- **Delete:** a red caret with the missing word written above it.
- **Not official:** a large red cross over the sheet.
- **Match:** a large green tick.
- **Unsure:** a pencil ring and a pencil question mark.
- **Partial:** a pencil bracket around what is visible.

Marks ride above the notice and never edit it. Each numbered pin pairs with a row in the written list, so a screen reader gets the same information.

### The Copy Switch
Your copy and Official share one sheet. Switching changes only the differing words and removes the marks, so the eye sees that nothing else moved.

### The Pen (motion)
The one authored moment. When a verdict lands, the ring or tick is drawn, the correction is written left to right, then the marks on the sheet appear, in about 1.5 seconds. Everything is readable before the pen moves. Reduced-motion users get the finished marks at once. Other transitions stay at 160ms.

## Do's and Don'ts

### Do:
- **Do** keep every text line on the rule.
- **Do** say "Cannot confirm" when the engine is unsure, in pencil.
- **Do** show the exact words that changed on every verdict.
- **Do** label fictional and sample content wherever someone could mistake it for real.

### Don't:
- **Don't** use red for errors, warnings, badges or emphasis.
- **Don't** show a confidence score, a percentage or a grade.
- **Don't** add shields, scanners, radar or AI sparkles.
- **Don't** add paper grain, curled corners, embossing or stamp effects.
- **Don't** use a mark to shame the person who forwarded a notice.
- **Don't** imitate the electoral body's look, or any party's colours or symbols.
- **Don't** use the hand font for interface copy.
