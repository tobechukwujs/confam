// Nigerian Pidgin (pcm). UNREVIEWED DRAFT written by an AI assistant, not a native speaker.
// Do not treat any string here as final until a native speaker has signed it off.
import type { Strings } from "./en";

export const pcm: Strings = {
  appName: "Confam",
  independence: "Independent checker. E no be INEC or any party.",
  languageMenu: "Language",
  skipLink: "Skip go di page",
  draftTranslation: "Draft translation",
  sampleNotice:
    "Example only. Dis notice na from di make-believe Simulated Electoral Commission, e no be real body.",

  home: {
    title: "Dis notice na true?",
    lead: "Paste di notice wey dem send you. We go put am beside di official record come mark wetin no match.",
    label: "Di notice text",
    placeholder: "Paste di notice here",
    submit: "Check dis notice",
    checking: "Dey check",
    errorEmpty: "Paste di notice text first.",
    errorTooLong: "Dat one too long. Paste di notice only (up to 5000 characters).",
    errorBusy: "Plenty checks dey now. Abeg try again after one minute.",
    errorDown: "We no fit reach di checker. Abeg try again.",
    samplesTitle: "See example of each answer",
    samplesNote: "Make-believe notices from di Simulated Electoral Commission.",
    samples: [
      { code: "C4NF7RM2", label: "Na true" },
      { code: "R3P7ACED", label: "Real, but dem don replace am" },
      { code: "A7T3R4ED", label: "Dem don change am: date" },
      { code: "A2NS3RTX", label: "Dem don change am: dem add line" },
      { code: "DX7K9PQA", label: "Dem don change am: word miss" },
      { code: "N9T6FFC7", label: "E no be official: wrong link" },
      { code: "P4RT7A2K", label: "Part only" },
      { code: "U5KN7WN3", label: "We no fit confirm: no dey record" },
      { code: "UNC7EAR2", label: "We no fit confirm: no clear" },
    ],
  },

  notFound: {
    title: "No check dey with dat code",
    body: "We no get any check wey carry dis code. If reply link come here but show dis message, e no come from Confam. We dey keep checks for 30 days.",
    back: "Check a notice",
  },

  upload: {
    heading: "Or check photo",
    lead: "Paste, drop or choose picture of di notice. We go read di words wey dey inside come check dem like pasted text.",
    choose: "Choose photo",
    camera: "Take photo",
    drop: "Drop di photo here, or paste am with Ctrl+V.",
    sending: "Dey send di photo",
    errorType: "Dat file no be picture wey we fit read. Use photo or screenshot (JPG, PNG or WebP).",
    errorSize: "Dat picture too big. Use one wey small pass 5 MB.",
    errorBusy: "Plenty checks dey now. Abeg try again after one minute.",
    errorDown: "We no fit reach di checker. Abeg try again.",
    errorOff: "Photo checks no dey work now. Abeg paste di text instead.",
  },

  reading: {
    title: "We dey read your notice",
    why: "We dey read di photo two times, we go only trust wetin both readings agree on.",
    stages: {
      queued: "Dey wait im turn",
      reading_1: "We dey read di photo, first time",
      reading_2: "We dey read am again, second time",
      comparing: "We dey compare am with di official record",
    },
    failed: "We no fit read dat photo. Try clearer one, or paste di text.",
    expired: "Dis check no dey here again. Abeg start again.",
    back: "Check another notice",
  },

  photo: {
    heading: "Your photo, wey we mark",
    note: "Na only you fit see dis photo. We no dey keep am.",
    alt: "Di photo wey you send, with marks where e no match di official notice",
  },

  record: {
    nav: "Official record",
    title: "Di official record",
    lead: "Every notice wey Confam dey check against, word for word, with who sign am.",
    asOf: "Record as of {date}",
    current: "Current notice",
    replacedBy: "Dem don replace am with {id}",
    published: "Published",
    idLabel: "Notice number",
    textHeading: "Exact text of di notice",
    textNote: "Dem show am word for word, for di language wey dem write am.",
    signedHeading: "Who sign am",
    first: "First signature",
    second: "Second signature",
    viewSource: "View source",
    back: "All notices",
    notFoundTitle: "No such notice",
    notFoundBody: "Dat notice number no dey di official record.",
  },

  verdict: {
    confirmed: {
      word: "Na true",
      sentence: "Dis one match di official notice.",
      instruction: "You fit pass am. Send am with dis check so people fit confirm am.",
      action: "Share am with dis check",
    },
    replaced: {
      word: "Real, but dem don replace am",
      sentence: "Dis one na official, but new notice don replace am.",
      instruction: "No act on am. Send di current notice instead.",
      action: "Send di current notice",
    },
    altered: {
      word: "Dem don change am",
      sentence: "Dis copy no be di same as di official notice.",
      instruction: "No pass dis copy. Send di correct one.",
      action: "Send di correct one",
    },
    not_official: {
      word: "E no be official",
      sentence: "Dis one talk something wey di official record no agree with.",
      instruction: "No act on am or pass am. Send di correct one.",
      action: "Send di correct one",
    },
    partial: {
      word: "Part only",
      sentence: "Part of di notice no dey here, so we check only wetin we fit see.",
      instruction: "Send di whole notice make we check all.",
      action: "See di whole notice",
    },
    cannot_confirm: {
      not_in_record: {
        word: "We no fit confirm",
        sentence: "We no see dis one for our record. Dat no mean say e be fake.",
        instruction: "Check again later, or ask di office wey issue am.",
        action: "Check another notice",
      },
      no_fact: {
        word: "We no fit confirm",
        sentence: "We no see anything for dis message wey we fit check with di record.",
        instruction: "Paste di notice itself, with im dates, figures or links.",
        action: "Check another notice",
      },
      unreadable: {
        word: "We no fit confirm",
        sentence: "We no fit read any word for dis photo.",
        instruction: "Send clearer photo, or paste di text.",
        action: "Send clearer photo",
      },
      unclear: {
        word: "We no fit confirm",
        sentence: "We no fit read dis one well enough to sure.",
        instruction: "Send clearer copy of di notice.",
        action: "Send clearer photo",
      },
      line_missing: {
        word: "We no fit confirm",
        sentence: "One line wey we need no dey dis copy.",
        instruction: "Send di whole notice.",
        action: "Send clearer photo",
      },
    },
  },

  changes: {
    heading: "Wetin change",
    none: "We no see any difference for di part wey we fit check.",
    replace: "Your copy talk say “{copy}”. Di official notice talk say “{official}”.",
    insert: "Your copy add “{copy}”. Di official notice no get am.",
    delete: "Your copy leave out “{official}”.",
    conflict: "Your copy talk say “{copy}”. Di official notice talk say “{official}”.",
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
    replacedIntro:
      "Your copy match one older official notice word for word. Di newer notice no be di same for here:",
    replacedNone: "New notice don replace am. Open am to see wetin different.",
    to: "go",
    rowInsert: "E dey only for di old notice: “{copy}”",
    rowDelete: "Dem add am for di newer notice: “{official}”",
    now: "now",
  },

  receipt: {
    heading: "Di receipt",
    notice: "Official notice",
    noNotice: "No official notice match",
    published: "Published",
    replacedBy: "Dem replace am with",
    replacedByValue: "{id}, published {date}",
    checked: "Checked",
    recordAsOf: "Record as of",
    code: "Check code",
    openOriginal: "Open di original",
    viewSource: "View source",
    verify: "Verify dis check",
  },

  share: {
    copied: "Dem don copy am. Paste am for di chat.",
    copyFailed: "E no copy. Copy di page address instead.",
    currentNoticeText: "Di current notice na {id}, published {date}.",
    correctNoticeText: "Di correct notice: {title}",
  },
};
