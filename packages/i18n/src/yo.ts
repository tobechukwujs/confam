// Yorùbá (yo). UNREVIEWED DRAFT written by an AI assistant, not a native speaker.
// Do not treat any string here as final until a native speaker has signed it off.
// Dotted letters (ẹ ọ ṣ) and tone marks must render (Andika latin-ext); the hand font never sets this text.
import type { Strings } from "./en";

export const yo: Strings = {
  appName: "Confam",
  independence: "Olùṣàyẹ̀wò tí kò ní ìbáṣepọ̀. Kì í ṣe INEC tàbí ẹgbẹ́ olóṣèlú kankan.",
  languageMenu: "Èdè",
  skipLink: "Lọ sí ojú ìwé náà",
  draftTranslation: "Ìtumọ̀ àkọ́kọ́",
  sampleNotice:
    "Àpẹẹrẹ nìkan ni. Ìkéde yìí wá láti Simulated Electoral Commission àròsọ, kì í ṣe àjọ gidi.",

  home: {
    title: "Ṣé òtítọ́ ni ìkéde yìí?",
    lead: "Lẹ ìkéde tí wọ́n fi ránṣẹ́ sí ọ. A ó gbé e lẹ́bàá ìwé àkọsílẹ̀ àṣẹ, a ó sì sàmì sí ohun tó yàtọ̀.",
    label: "Ọ̀rọ̀ inú ìkéde náà",
    placeholder: "Lẹ ìkéde náà síbí",
    submit: "Ṣàyẹ̀wò ìkéde yìí",
    checking: "Ń ṣàyẹ̀wò",
    errorEmpty: "Kọ́kọ́ lẹ ọ̀rọ̀ inú ìkéde náà.",
    errorTooLong: "Ó gùn jù. Lẹ ìkéde náà nìkan (títí dé ọ̀rọ̀ 5000).",
    errorBusy: "Àyẹ̀wò pọ̀ jù báyìí. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i lẹ́yìn ìṣẹ́jú kan.",
    errorDown: "A kò lè dé ibi àyẹ̀wò. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i.",
    samplesTitle: "Wo àpẹẹrẹ ìdáhùn kọ̀ọ̀kan",
    samplesNote: "Àwọn ìkéde àròsọ láti Simulated Electoral Commission.",
    samples: [
      { code: "C4NF7RM2", label: "A ti jẹ́rìí rẹ̀" },
      { code: "R3P7ACED", label: "Òtítọ́ ni, ṣùgbọ́n a ti rọ́pò rẹ̀" },
      { code: "A7T3R4ED", label: "A ti yí i padà: ọjọ́ tí a yí" },
      { code: "A2NS3RTX", label: "A ti yí i padà: a fi ìlà kún un" },
      { code: "DX7K9PQA", label: "A ti yí i padà: ọ̀rọ̀ kan sọnù" },
      { code: "N9T6FFC7", label: "Kì í ṣe ti àṣẹ: ìjápọ̀ tí kò tọ́" },
      { code: "P4RT7A2K", label: "Apá kan péré" },
      { code: "U5KN7WN3", label: "A kò lè jẹ́rìí rẹ̀: kò sí nínú ìwé àkọsílẹ̀" },
      { code: "UNC7EAR2", label: "A kò lè jẹ́rìí rẹ̀: kò hàn kedere" },
    ],
  },

  notFound: {
    title: "Kò sí àyẹ̀wò pẹ̀lú kóòdù yẹn",
    body: "A kò ní àkọsílẹ̀ àyẹ̀wò kankan pẹ̀lú kóòdù yìí. Ìdáhùn tó bá mú ọ wá síbí ṣùgbọ́n tó fi ìfiránṣẹ́ yìí hàn kò wá láti Confam. À ń tọ́jú àyẹ̀wò fún ọjọ́ 30.",
    back: "Ṣàyẹ̀wò ìkéde",
  },

  upload: {
    heading: "Tàbí ṣàyẹ̀wò fọ́tò",
    lead: "Lẹ̀, fà sílẹ̀ tàbí yan àwòrán ìkéde náà. A ó ka àwọn ọ̀rọ̀ inú rẹ̀, a ó sì ṣàyẹ̀wò wọn bí ọ̀rọ̀ tí a lẹ̀.",
    choose: "Yan fọ́tò",
    camera: "Ya fọ́tò",
    drop: "Fà fọ́tò náà sílẹ̀ síbí, tàbí lẹ̀ ẹ́ pẹ̀lú Ctrl+V.",
    sending: "Ń fi fọ́tò náà ránṣẹ́",
    errorType: "Fáìlì yẹn kì í ṣe àwòrán tí a lè kà. Lo fọ́tò tàbí àwòrán ojú ìwé (JPG, PNG tàbí WebP).",
    errorSize: "Àwòrán yẹn tóbi jù. Lo èyí tí kò tó 5 MB.",
    errorBusy: "Àyẹ̀wò pọ̀ jù báyìí. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i lẹ́yìn ìṣẹ́jú kan.",
    errorDown: "A kò lè dé ibi àyẹ̀wò. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i.",
    errorOff: "Àyẹ̀wò fọ́tò kò sí lọ́wọ́lọ́wọ́. Jọ̀wọ́ lẹ ọ̀rọ̀ inú ìkéde dípò rẹ̀.",
  },

  reading: {
    title: "À ń ka ìkéde rẹ",
    why: "À ń ka fọ́tò náà lẹ́ẹ̀mejì, a sì ń gbẹ́kẹ̀lé ohun tí ìkàwé méjèèjì fohùn ṣọ̀kan lé lórí nìkan.",
    stages: {
      queued: "Ó ń dúró dè àkókò rẹ̀",
      reading_1: "À ń ka fọ́tò náà, ìgbà àkọ́kọ́",
      reading_2: "À ń tún un ka, ìgbà kejì",
      comparing: "À ń fi wé ìwé àkọsílẹ̀ àṣẹ",
    },
    failed: "A kò lè ka fọ́tò yẹn. Gbìyànjú èyí tó mọ́ gaara, tàbí lẹ ọ̀rọ̀ inú rẹ̀.",
    expired: "Àyẹ̀wò yìí kò sí níbí mọ́. Jọ̀wọ́ bẹ̀rẹ̀ lẹ́ẹ̀kan sí i.",
    back: "Ṣàyẹ̀wò ìkéde mìíràn",
  },

  photo: {
    heading: "Fọ́tò rẹ, tí a sàmì sí",
    note: "Ìwọ nìkan ló lè rí fọ́tò yìí. A kì í tọ́jú rẹ̀.",
    alt: "Fọ́tò tí o fi ránṣẹ́, pẹ̀lú àmì níbi tó ti yàtọ̀ sí ìkéde àṣẹ",
  },

  record: {
    nav: "Ìwé àkọsílẹ̀ àṣẹ",
    title: "Ìwé àkọsílẹ̀ àṣẹ",
    lead: "Gbogbo ìkéde tí Confam fi ń ṣàyẹ̀wò, ọ̀rọ̀ fún ọ̀rọ̀, pẹ̀lú àwọn tó buwọ́ lù ú.",
    asOf: "Ìwé àkọsílẹ̀ títí di {date}",
    current: "Ìkéde lọ́wọ́lọ́wọ́",
    replacedBy: "A ti fi {id} rọ́pò rẹ̀",
    published: "Ọjọ́ tí a tẹ̀ ẹ́ jáde",
    idLabel: "Nọ́ńbà ìkéde",
    textHeading: "Ọ̀rọ̀ gangan inú ìkéde náà",
    textNote: "A fi hàn ọ̀rọ̀ fún ọ̀rọ̀, ní èdè tí a fi kọ ọ́.",
    signedHeading: "Àwọn tó buwọ́ lù ú",
    first: "Ìbuwọ́lù àkọ́kọ́",
    second: "Ìbuwọ́lù kejì",
    viewSource: "Wo orísun",
    back: "Gbogbo ìkéde",
    notFoundTitle: "Kò sí ìkéde bẹ́ẹ̀",
    notFoundBody: "Nọ́ńbà ìkéde yẹn kò sí nínú ìwé àkọsílẹ̀ àṣẹ.",
  },

  verdict: {
    confirmed: {
      word: "A ti jẹ́rìí rẹ̀",
      sentence: "Èyí bá ìkéde àṣẹ náà mu.",
      instruction: "O lè pín in. Fi àyẹ̀wò yìí rán an kí àwọn mìíràn lè fìdí rẹ̀ múlẹ̀.",
      action: "Pín in pẹ̀lú àyẹ̀wò yìí",
    },
    replaced: {
      word: "Òtítọ́ ni, ṣùgbọ́n a ti rọ́pò rẹ̀",
      sentence: "Ìkéde àṣẹ ni èyí, ṣùgbọ́n ìkéde tuntun ti rọ́pò rẹ̀.",
      instruction: "Má ṣe gbé ìgbésẹ̀ lórí rẹ̀. Fi ìkéde lọ́wọ́lọ́wọ́ ránṣẹ́ dípò rẹ̀.",
      action: "Fi ìkéde lọ́wọ́lọ́wọ́ ránṣẹ́",
    },
    altered: {
      word: "A ti yí i padà",
      sentence: "Ẹ̀dà yìí yàtọ̀ sí ìkéde àṣẹ náà.",
      instruction: "Má ṣe tan ẹ̀dà yìí kálẹ̀. Fi èyí tó tọ́ ránṣẹ́.",
      action: "Fi èyí tó tọ́ ránṣẹ́",
    },
    not_official: {
      word: "Kì í ṣe ti àṣẹ",
      sentence: "Èyí sọ ohun tí ìwé àkọsílẹ̀ àṣẹ tako.",
      instruction: "Má ṣe gbé ìgbésẹ̀ lórí rẹ̀ tàbí tan án kálẹ̀. Fi èyí tó tọ́ ránṣẹ́.",
      action: "Fi èyí tó tọ́ ránṣẹ́",
    },
    partial: {
      word: "Apá kan péré",
      sentence: "Apá kan lára ìkéde náà kò sí níbí, nítorí náà a ṣàyẹ̀wò ohun tí a rí nìkan.",
      instruction: "Fi odindi ìkéde náà ránṣẹ́ kí a lè ṣàyẹ̀wò gbogbo rẹ̀.",
      action: "Wo odindi ìkéde náà",
    },
    cannot_confirm: {
      not_in_record: {
        word: "A kò lè jẹ́rìí rẹ̀",
        sentence: "A kò rí èyí nínú ìwé àkọsílẹ̀ wa. Ìyẹn kò túmọ̀ sí pé irọ́ ni.",
        instruction: "Ṣàyẹ̀wò lẹ́ẹ̀kan sí i lẹ́yìn náà, tàbí béèrè lọ́wọ́ ọ́fíìsì tó gbé e jáde.",
        action: "Ṣàyẹ̀wò ìkéde mìíràn",
      },
      no_fact: {
        word: "A kò lè jẹ́rìí rẹ̀",
        sentence: "A kò rí nǹkan kan nínú ìfiránṣẹ́ yìí tí a lè fi ṣàyẹ̀wò pẹ̀lú ìwé àkọsílẹ̀.",
        instruction: "Lẹ ìkéde fúnra rẹ̀, pẹ̀lú ọjọ́, nọ́ńbà tàbí ìjápọ̀ rẹ̀.",
        action: "Ṣàyẹ̀wò ìkéde mìíràn",
      },
      unreadable: {
        word: "A kò lè jẹ́rìí rẹ̀",
        sentence: "A kò lè ka ọ̀rọ̀ kankan lórí fọ́tò yìí.",
        instruction: "Fi fọ́tò tó mọ́ gaara ránṣẹ́, tàbí lẹ ọ̀rọ̀ inú rẹ̀.",
        action: "Fi fọ́tò tó mọ́ ránṣẹ́",
      },
      unclear: {
        word: "A kò lè jẹ́rìí rẹ̀",
        sentence: "A kò lè ka èyí dáadáa tó láti dá wa lójú.",
        instruction: "Fi ẹ̀dà tó mọ́ gaara ránṣẹ́.",
        action: "Fi fọ́tò tó mọ́ ránṣẹ́",
      },
      line_missing: {
        word: "A kò lè jẹ́rìí rẹ̀",
        sentence: "Ìlà kan tí a nílò kò sí nínú ẹ̀dà yìí.",
        instruction: "Fi odindi ìkéde náà ránṣẹ́.",
        action: "Fi fọ́tò tó mọ́ ránṣẹ́",
      },
    },
  },

  changes: {
    heading: "Ohun tó yípadà",
    none: "A kò rí ìyàtọ̀ kankan nínú apá tí a lè ṣàyẹ̀wò.",
    replace: "Ẹ̀dà rẹ sọ pé “{copy}”. Ìkéde àṣẹ sọ pé “{official}”.",
    insert: "Ẹ̀dà rẹ fi “{copy}” kún un. Ìkéde àṣẹ kò ní i.",
    delete: "Ẹ̀dà rẹ fi “{official}” sílẹ̀.",
    conflict: "Ẹ̀dà rẹ sọ pé “{copy}”. Ìkéde àṣẹ sọ pé “{official}”.",
    kinds: {
      date: "Ọjọ́",
      time: "Àkókò",
      weekday: "Ọjọ́ ọ̀sẹ̀",
      number: "Nọ́ńbà",
      money: "Owó",
      link: "Ìjápọ̀",
      phone: "Nọ́ńbà fóònù",
      negation: "Ìtumọ̀",
      text: "Ọ̀rọ̀",
    },
    conflictKinds: { date: "Ọjọ́", link: "Ìjápọ̀", money: "Owó" },
    replacedIntro:
      "Ẹ̀dà rẹ bá ìkéde àṣẹ àtijọ́ mu ọ̀rọ̀ fún ọ̀rọ̀. Ìkéde tuntun yàtọ̀ níbí:",
    replacedNone: "Ìkéde tuntun ti rọ́pò rẹ̀. Ṣí i láti wo àwọn ìyàtọ̀.",
    to: "sí",
    rowInsert: "Inú ìkéde àtijọ́ nìkan ló wà: “{copy}”",
    rowDelete: "A fi kún ìkéde tuntun: “{official}”",
    now: "báyìí",
  },

  receipt: {
    heading: "Ìwé ẹ̀rí",
    notice: "Ìkéde àṣẹ",
    noNotice: "Kò sí ìkéde àṣẹ tó bá a mu",
    published: "Ọjọ́ tí a tẹ̀ ẹ́ jáde",
    replacedBy: "A ti fi rọ́pò rẹ̀",
    replacedByValue: "{id}, a tẹ̀ ẹ́ jáde ní {date}",
    checked: "A ṣàyẹ̀wò",
    recordAsOf: "Ìwé àkọsílẹ̀ títí di",
    code: "Kóòdù àyẹ̀wò",
    openOriginal: "Ṣí ìkéde àkọ́kọ́",
    viewSource: "Wo orísun",
    verify: "Fìdí àyẹ̀wò yìí múlẹ̀",
  },

  share: {
    copied: "A ti dà á kọ. Lẹ̀ ẹ́ mọ́ ìjíròrò náà.",
    copyFailed: "A kò lè dà á kọ. Dà àdírẹ́sì ojú ìwé náà kọ dípò rẹ̀.",
    currentNoticeText: "Ìkéde lọ́wọ́lọ́wọ́ ni {id}, a tẹ̀ ẹ́ jáde ní {date}.",
    correctNoticeText: "Ìkéde tó tọ́: {title}",
  },
};
