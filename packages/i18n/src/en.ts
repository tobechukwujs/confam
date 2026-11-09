// English strings. Rule 4: no scores, percentages or grades in any string.
// Non-English locales are TODO and need native-speaker review before they ship.

export type VerdictCopy = {
  word: string;
  sentence: string;
  instruction: string;
  action: string;
};

export const en = {
  appName: "Confam",
  independence: "Independent checker. Not INEC or any party.",
  languageName: "English",
  draftTranslation: "Draft translation",
  sampleNotice:
    "Sample only. This notice is from the fictional Simulated Electoral Commission, not a real body.",

  home: {
    title: "Is this notice real?",
    lead: "Paste the notice you were sent. We lay it beside the official record and mark what is different.",
    label: "The notice text",
    placeholder: "Paste the notice here",
    submit: "Check this notice",
    checking: "Checking",
    errorEmpty: "Paste the notice text first.",
    errorTooLong: "That is too long. Paste the notice only (up to 5000 characters).",
    errorBusy: "Too many checks just now. Please try again in a minute.",
    errorDown: "We could not reach the checker. Please try again.",
    samplesTitle: "See a sample of each answer",
    samplesNote: "Fictional notices from the Simulated Electoral Commission.",
    // Codes match fixtures/sec-sim/sample-verdicts.json.
    samples: [
      { code: "C4NF7RM2", label: "Confirmed" },
      { code: "R3P7ACED", label: "Real, but replaced" },
      { code: "A7T3R4ED", label: "Altered: a changed date" },
      { code: "A2NS3RTX", label: "Altered: an added line" },
      { code: "DX7K9PQA", label: "Altered: a missing word" },
      { code: "N9T6FFC7", label: "Not official: a wrong link" },
      { code: "P4RT7A2K", label: "Partial" },
      { code: "U5KN7WN3", label: "Cannot confirm: not in the record" },
      { code: "UNC7EAR2", label: "Cannot confirm: unclear" },
    ],
  },

  notFound: {
    title: "No check with that code",
    body: "We have no record of a check with this code. A reply that links here but shows this message is not from Confam. Checks are kept for 30 days.",
    back: "Check a notice",
  },

  record: {
    nav: "Official record",
    title: "The official record",
    lead: "Every notice Confam checks against, word for word, with who signed it.",
    asOf: "Record as of {date}",
    current: "Current notice",
    replacedBy: "Replaced by {id}",
    published: "Published",
    idLabel: "Notice number",
    textHeading: "Exact text of the notice",
    textNote: "Shown word for word, in the language it was written in.",
    signedHeading: "Signed by",
    first: "First signature",
    second: "Second signature",
    viewSource: "View source",
    back: "All notices",
    notFoundTitle: "No such notice",
    notFoundBody: "That notice number is not in the official record.",
  },

  verdict: {
    confirmed: {
      word: "Confirmed",
      sentence: "This matches the official notice.",
      instruction: "It is safe to pass on. Send it with this check so others can verify it.",
      action: "Share it with this check",
    },
    replaced: {
      word: "Real, but replaced",
      sentence: "This was official, but a newer notice has replaced it.",
      instruction: "Do not act on it. Send the current notice instead.",
      action: "Send the current notice",
    },
    altered: {
      word: "Altered",
      sentence: "This copy is different from the official notice.",
      instruction: "Do not pass this copy on. Send the correct one.",
      action: "Send the correct one",
    },
    not_official: {
      word: "Not official",
      sentence: "This says something the official record contradicts.",
      instruction: "Do not act on it or pass it on. Send the correct one.",
      action: "Send the correct one",
    },
    partial: {
      word: "Partial",
      sentence: "Part of the notice is missing, so we checked only what is visible.",
      instruction: "Send the whole notice to check all of it.",
      action: "See the whole notice",
    },
    cannot_confirm: {
      not_in_record: {
        word: "Cannot confirm",
        sentence: "We could not find this in our record. That does not mean it is fake.",
        instruction: "Check again later, or ask the office that issued it.",
        action: "Check another notice",
      },
      no_fact: {
        word: "Cannot confirm",
        sentence: "We found nothing in this message that we can check against the record.",
        instruction: "Paste the notice itself, with its dates, figures or links.",
        action: "Check another notice",
      },
      unclear: {
        word: "Cannot confirm",
        sentence: "We could not read this clearly enough to be sure.",
        instruction: "Send a clearer copy of the notice.",
        action: "Send a clearer photo",
      },
      line_missing: {
        word: "Cannot confirm",
        sentence: "A line we need is missing from this copy.",
        instruction: "Send the whole notice.",
        action: "Send a clearer photo",
      },
    },
  },

  changes: {
    heading: "What changed",
    none: "No differences found in the part we could check.",
    replace: "Your copy says “{copy}”. The official notice says “{official}”.",
    insert: "Your copy adds “{copy}”. The official notice does not have it.",
    delete: "Your copy leaves out “{official}”.",
    conflict: "Your copy says “{copy}”. The official notice says “{official}”.",
    kinds: {
      date: "Date",
      time: "Time",
      weekday: "Day",
      number: "Number",
      money: "Money",
      link: "Link",
      phone: "Phone number",
      negation: "Meaning",
      text: "Words",
    },
    conflictKinds: { date: "Date", link: "Link", money: "Money" },
    // Replaced notice: the copy matches an OLD notice. copy = old value, official = new value.
    replacedIntro: "Your copy matches an older official notice word for word. The newer notice differs here:",
    replacedNone: "A newer notice has replaced it. Open it to see the differences.",
    rowReplace: "{copy} → {official}",
    rowInsert: "Only in the old notice: “{copy}”",
    rowDelete: "Added in the newer notice: “{official}”",
    now: "now",
  },

  receipt: {
    heading: "The receipt",
    notice: "Official notice",
    noNotice: "No official notice matched",
    published: "Published",
    replacedBy: "Replaced by",
    replacedByValue: "{id}, published {date}",
    checked: "Checked",
    recordAsOf: "Record as of",
    code: "Check code",
    openOriginal: "Open the original",
    viewSource: "View source",
    verify: "Verify this check",
  },

  share: {
    copied: "Copied. Paste it in the chat.",
    copyFailed: "Could not copy. Copy the page address instead.",
    currentNoticeText: "The current notice is {id}, published {date}.",
    correctNoticeText: "The correct notice: {title}",
  },
};

export type Strings = typeof en;
