// Hausa (ha). UNREVIEWED DRAFT written by an AI assistant, not a native speaker.
// Do not treat any string here as final until a native speaker has signed it off.
// Hooked letters ɓ ɗ ƙ must render (Andika latin-ext). Playwrite NG Modern lacks them and is never used here.
import type { Strings } from "./en";

export const ha: Strings = {
  appName: "Confam",
  independence: "Mai bincike mai zaman kansa. Ba INEC ko wata jam'iyya ba ce.",
  languageMenu: "Harshe",
  skipLink: "Tsallaka zuwa shafin",
  draftTranslation: "Fassarar gwaji",
  sampleNotice:
    "Misali kawai. Wannan sanarwar ta fito ne daga hukumar zaɓe ta ƙage, Simulated Electoral Commission, ba hukuma ta gaske ba.",

  home: {
    title: "Wannan sanarwar gaskiya ce?",
    lead: "Liƙa sanarwar da aka aiko maka. Za mu ajiye ta kusa da bayanan hukuma mu yi alama a inda ta bambanta.",
    label: "Rubutun sanarwar",
    placeholder: "Liƙa sanarwar a nan",
    submit: "Duba wannan sanarwar",
    checking: "Ana dubawa",
    errorEmpty: "Da farko ka liƙa rubutun sanarwar.",
    errorTooLong: "Wannan ya yi tsayi da yawa. Ka liƙa sanarwar kawai (har haruffa 5000).",
    errorBusy: "Ana yawan bincike a yanzu. Ka sake gwadawa bayan minti ɗaya.",
    errorDown: "Ba mu iya isa ga mai bincike ba. Ka sake gwadawa.",
    samplesTitle: "Duba misali na kowace amsa",
    samplesNote: "Sanarwoyin ƙage daga Simulated Electoral Commission.",
    samples: [
      { code: "C4NF7RM2", label: "An tabbatar" },
      { code: "R3P7ACED", label: "Na gaskiya ne, amma an maye gurbinsa" },
      { code: "A7T3R4ED", label: "An canza: ranar da aka canza" },
      { code: "A2NS3RTX", label: "An canza: an ƙara layi" },
      { code: "DX7K9PQA", label: "An canza: kalma ta ɓace" },
      { code: "N9T6FFC7", label: "Ba na hukuma ba ne: hanyar haɗi ta ƙarya" },
      { code: "P4RT7A2K", label: "Ɓangare kawai" },
      { code: "U5KN7WN3", label: "Ba mu iya tabbatarwa ba: ba a bayanai ba" },
      { code: "UNC7EAR2", label: "Ba mu iya tabbatarwa ba: ba a gani sosai ba" },
    ],
  },

  notFound: {
    title: "Babu bincike mai wannan lambar",
    body: "Ba mu da wani bincike mai wannan lambar. Idan amsa ta kai ka nan amma tana nuna wannan saƙon, ba daga Confam ta fito ba. Muna adana bincike na kwana 30.",
    back: "Duba wata sanarwa",
  },

  record: {
    nav: "Bayanan hukuma",
    title: "Bayanan hukuma",
    lead: "Kowace sanarwa da Confam ke dubawa da ita, kalma da kalma, tare da waɗanda suka sa hannu.",
    asOf: "Bayanan har zuwa {date}",
    current: "Sanarwar yanzu",
    replacedBy: "An maye gurbinta da {id}",
    published: "Ranar bugawa",
    idLabel: "Lambar sanarwa",
    textHeading: "Ainihin rubutun sanarwar",
    textNote: "An nuna shi kalma da kalma, a cikin harshen da aka rubuta shi.",
    signedHeading: "Waɗanda suka sa hannu",
    first: "Sa hannu na farko",
    second: "Sa hannu na biyu",
    viewSource: "Duba tushe",
    back: "Dukan sanarwoyi",
    notFoundTitle: "Babu irin wannan sanarwa",
    notFoundBody: "Wannan lambar sanarwar ba ta cikin bayanan hukuma.",
  },

  verdict: {
    confirmed: {
      word: "An tabbatar",
      sentence: "Wannan ya yi daidai da sanarwar hukuma.",
      instruction: "Za ka iya raba shi. Ka aika shi tare da wannan bincike don wasu su tabbatar.",
      action: "Raba shi da wannan bincike",
    },
    replaced: {
      word: "Gaskiya ne, an maye shi",
      sentence: "Wannan na hukuma ne, amma sabuwar sanarwa ta maye gurbinsa.",
      instruction: "Kada ka yi aiki da shi. Ka aika sanarwar yanzu maimakon haka.",
      action: "Aika sanarwar yanzu",
    },
    altered: {
      word: "An canza shi",
      sentence: "Wannan kwafi ya bambanta da sanarwar hukuma.",
      instruction: "Kada ka yaɗa wannan kwafi. Ka aika wanda ya dace.",
      action: "Aika wanda ya dace",
    },
    not_official: {
      word: "Ba na hukuma ba ne",
      sentence: "Wannan yana cewa abin da bayanan hukuma suka ƙaryata.",
      instruction: "Kada ka yi aiki da shi ko ka yaɗa shi. Ka aika wanda ya dace.",
      action: "Aika wanda ya dace",
    },
    partial: {
      word: "Ɓangare kawai",
      sentence: "Wani ɓangare na sanarwar ya ɓace, don haka mun duba abin da ake gani ne kawai.",
      instruction: "Ka aika dukan sanarwar don mu duba duka.",
      action: "Duba dukan sanarwar",
    },
    cannot_confirm: {
      not_in_record: {
        word: "Ba mu iya tabbatarwa ba",
        sentence: "Ba mu same shi a bayananmu ba. Hakan ba yana nufin ƙarya ne ba.",
        instruction: "Ka sake dubawa daga baya, ko ka tambayi ofishin da ya bayar da shi.",
        action: "Duba wata sanarwa",
      },
      no_fact: {
        word: "Ba mu iya tabbatarwa ba",
        sentence: "Ba mu sami wani abu a wannan saƙon da za mu iya dubawa da bayanan hukuma ba.",
        instruction: "Ka liƙa sanarwar kanta, da kwanakinta, lambobinta ko hanyoyin haɗinta.",
        action: "Duba wata sanarwa",
      },
      unclear: {
        word: "Ba mu iya tabbatarwa ba",
        sentence: "Ba mu iya karanta wannan da kyau ba don mu tabbata.",
        instruction: "Ka aika kwafi mai haske na sanarwar.",
        action: "Aika hoto mai haske",
      },
      line_missing: {
        word: "Ba mu iya tabbatarwa ba",
        sentence: "Wani layi da muke buƙata ya ɓace daga wannan kwafi.",
        instruction: "Ka aika dukan sanarwar.",
        action: "Aika hoto mai haske",
      },
    },
  },

  changes: {
    heading: "Abin da ya canza",
    none: "Ba mu sami bambanci a ɓangaren da muka iya dubawa ba.",
    replace: "Kwafinka ya ce “{copy}”. Sanarwar hukuma ta ce “{official}”.",
    insert: "Kwafinka ya ƙara “{copy}”. Sanarwar hukuma ba ta da shi.",
    delete: "Kwafinka ya bar “{official}”.",
    conflict: "Kwafinka ya ce “{copy}”. Sanarwar hukuma ta ce “{official}”.",
    kinds: {
      date: "Kwanan wata",
      time: "Lokaci",
      weekday: "Rana",
      number: "Lamba",
      money: "Kuɗi",
      link: "Hanyar haɗi",
      phone: "Lambar waya",
      negation: "Ma'ana",
      text: "Kalmomi",
    },
    conflictKinds: { date: "Kwanan wata", link: "Hanyar haɗi", money: "Kuɗi" },
    replacedIntro:
      "Kwafinka ya yi daidai da tsohuwar sanarwar hukuma kalma da kalma. Sabuwar sanarwar ta bambanta a nan:",
    replacedNone: "Sabuwar sanarwa ta maye gurbinsa. Ka buɗe ta don ganin bambance-bambancen.",
    to: "zuwa",
    rowInsert: "Yana cikin tsohuwar sanarwar kawai: “{copy}”",
    rowDelete: "An ƙara shi a sabuwar sanarwar: “{official}”",
    now: "yanzu",
  },

  receipt: {
    heading: "Takardar shaida",
    notice: "Sanarwar hukuma",
    noNotice: "Babu sanarwar hukuma da ta dace",
    published: "Ranar bugawa",
    replacedBy: "An maye gurbinta da",
    replacedByValue: "{id}, an buga ta {date}",
    checked: "An duba",
    recordAsOf: "Bayanan har zuwa",
    code: "Lambar bincike",
    openOriginal: "Buɗe ainihin sanarwar",
    viewSource: "Duba tushe",
    verify: "Tabbatar da wannan bincike",
  },

  share: {
    copied: "An kwafa. Ka liƙa shi a cikin hira.",
    copyFailed: "Ba a iya kwafawa ba. Ka kwafi adireshin shafin maimakon haka.",
    currentNoticeText: "Sanarwar yanzu ita ce {id}, an buga ta {date}.",
    correctNoticeText: "Sanarwar da ta dace: {title}",
  },
};
