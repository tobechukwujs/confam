// Igbo (ig). UNREVIEWED DRAFT written by an AI assistant, not a native speaker.
// Do not treat any string here as final until a native speaker has signed it off.
// Dotted letters (ị ọ ụ) and ṅ must render (Andika latin-ext); the hand font never sets this text.
import type { Strings } from "./en";

export const ig: Strings = {
  appName: "Confam",
  independence: "Onye nlele nọọrọ onwe ya. Ọ bụghị INEC ma ọ bụ otu ọ bụla.",
  languageMenu: "Asụsụ",
  skipLink: "Gafee gaa ibe ahụ",
  draftTranslation: "Nsụgharị mbụ",
  sampleNotice:
    "Ihe atụ naanị. Ọkwa a sitere na Simulated Electoral Commission nke e chepụtara echepụta, ọ bụghị ụlọ ọrụ n'ezie.",

  home: {
    title: "Ọkwa a ọ bụ eziokwu?",
    lead: "Tinye ọkwa e zitere gị. Anyị ga-etinye ya n'akụkụ ndekọ gọọmentị ma kaa akara ebe ọ dị iche.",
    label: "Ederede ọkwa ahụ",
    placeholder: "Tinye ọkwa ahụ ebe a",
    submit: "Lelee ọkwa a",
    checking: "Na-elele",
    errorEmpty: "Ṅaa ntị: buru ụzọ tinye ederede ọkwa ahụ.",
    errorTooLong: "Ọ toro ogologo. Tinye ọkwa ahụ naanị (ruo mkpụrụedemede 5000).",
    errorBusy: "Nlele dị ọtụtụ ugbu a. Biko nwaa ọzọ mgbe nkeji otu gasịrị.",
    errorDown: "Anyị enweghị ike iru ebe nlele. Biko nwaa ọzọ.",
    samplesTitle: "Hụ ihe atụ nke azịza ọ bụla",
    samplesNote: "Ọkwa e chepụtara echepụta sitere na Simulated Electoral Commission.",
    samples: [
      { code: "C4NF7RM2", label: "Akwadoro ya" },
      { code: "R3P7ACED", label: "Ọ bụ eziokwu, mana e dochiela ya" },
      { code: "A7T3R4ED", label: "Agbanwere ya: ụbọchị" },
      { code: "A2NS3RTX", label: "Agbanwere ya: agbakwunyere ahịrị" },
      { code: "DX7K9PQA", label: "Agbanwere ya: okwu na-efu" },
      { code: "N9T6FFC7", label: "Ọ bụghị nke gọọmentị: njikọ ezighi ezi" },
      { code: "P4RT7A2K", label: "Akụkụ naanị" },
      { code: "U5KN7WN3", label: "Anyị enweghị ike ikwado ya: ọ nọghị n'ndekọ" },
      { code: "UNC7EAR2", label: "Anyị enweghị ike ikwado ya: ọ doghị anya" },
    ],
  },

  notFound: {
    title: "Enweghị nlele nwere koodu ahụ",
    body: "Anyị enweghị ndekọ nlele ọ bụla nwere koodu a. Azịza nke kpọtara gị ebe a mana na-egosi ozi a abụghị nke si na Confam. Anyị na-edebe nlele ruo ụbọchị 30.",
    back: "Lelee ọkwa",
  },

  upload: {
    heading: "Ma ọ bụ lelee foto",
    lead: "Tinye, tụdo ma ọ bụ họrọ foto ọkwa ahụ. Anyị ga-agụ okwu ndị dị na ya ma lelee ha dị ka ederede e tinyere.",
    choose: "Họrọ foto",
    camera: "See foto",
    drop: "Tụdo foto ahụ ebe a, ma ọ bụ tinye ya site na Ctrl+V.",
    sending: "Na-ezipụ foto ahụ",
    errorType: "Faịlụ ahụ abụghị foto anyị nwere ike ịgụ. Jiri foto ma ọ bụ foto ihuenyo (JPG, PNG ma ọ bụ WebP).",
    errorSize: "Foto ahụ buru ibu. Jiri nke dị ntakịrị karịa 5 MB.",
    errorBusy: "Nlele dị ọtụtụ ugbu a. Biko nwaa ọzọ mgbe nkeji otu gasịrị.",
    errorDown: "Anyị enweghị ike iru ebe nlele. Biko nwaa ọzọ.",
    errorOff: "Nlele foto adịghị ugbu a. Biko tinye ederede kama.",
  },

  reading: {
    title: "Na-agụ ọkwa gị",
    why: "Anyị na-agụ foto ahụ ugboro abụọ, ma anyị na-ekwere naanị ihe ọgụgụ abụọ ahụ kwenyere na ya.",
    stages: {
      queued: "Na-eche oge ya",
      reading_1: "Na-agụ foto ahụ, nke mbụ",
      reading_2: "Na-agụ ya ọzọ, nke abụọ",
      comparing: "Na-eji ya tụnyere ndekọ gọọmentị",
    },
    failed: "Anyị enweghị ike ịgụ foto ahụ. Nwaa nke doro anya, ma ọ bụ tinye ederede.",
    expired: "Nlele a adịghị ebe a ọzọ. Biko malite ọzọ.",
    back: "Lelee ọkwa ọzọ",
  },

  photo: {
    heading: "Foto gị, e kaara akara",
    note: "Naanị gị nwere ike ịhụ foto a. Anyị anaghị edebe ya.",
    alt: "Foto i zitere, nwere akara ebe ọ dị iche na ọkwa gọọmentị",
  },

  record: {
    nav: "Ndekọ gọọmentị",
    title: "Ndekọ gọọmentị",
    lead: "Ọkwa niile Confam na-eji lelee, okwu site n'okwu, ya na ndị bịanyere aka.",
    asOf: "Ndekọ ruo {date}",
    current: "Ọkwa nke ugbu a",
    replacedBy: "E dochiela ya na {id}",
    published: "Ụbọchị e bipụtara",
    idLabel: "Nọmba ọkwa",
    textHeading: "Ederede kpọmkwem nke ọkwa ahụ",
    textNote: "E gosiri ya okwu site n'okwu, n'asụsụ e ji dee ya.",
    signedHeading: "Ndị bịanyere aka",
    first: "Aka mbụ",
    second: "Aka nke abụọ",
    viewSource: "Lee isi mmalite",
    back: "Ọkwa niile",
    notFoundTitle: "Enweghị ọkwa dị otú ahụ",
    notFoundBody: "Nọmba ọkwa ahụ adịghị n'ndekọ gọọmentị.",
  },

  verdict: {
    confirmed: {
      word: "Akwadoro ya",
      sentence: "Nke a dabara na ọkwa gọọmentị.",
      instruction: "Ị nwere ike ịkesa ya. Zipụ ya na nlele a ka ndị ọzọ nwee ike ịkwado ya.",
      action: "Kesaa ya na nlele a",
    },
    replaced: {
      word: "Eziokwu, mana e dochiela ya",
      sentence: "Nke a bụ ọkwa gọọmentị, mana ọkwa ọhụrụ edochiela ya.",
      instruction: "Emela ihe site na ya. Zipụ ọkwa nke ugbu a kama.",
      action: "Zipụ ọkwa nke ugbu a",
    },
    altered: {
      word: "Agbanwere ya",
      sentence: "Mbipụta a dị iche na ọkwa gọọmentị.",
      instruction: "Ekesala mbipụta a. Zipụ nke ziri ezi.",
      action: "Zipụ nke ziri ezi",
    },
    not_official: {
      word: "Ọ bụghị nke gọọmentị",
      sentence: "Nke a na-ekwu ihe ndekọ gọọmentị megidere.",
      instruction: "Emela ihe site na ya ma ọ bụ kesaa ya. Zipụ nke ziri ezi.",
      action: "Zipụ nke ziri ezi",
    },
    partial: {
      word: "Akụkụ naanị",
      sentence: "Akụkụ nke ọkwa ahụ efunahụla, ya mere anyị lelere naanị ihe a na-ahụ.",
      instruction: "Zipụ ọkwa niile ka anyị lelee ya nile.",
      action: "Hụ ọkwa niile",
    },
    cannot_confirm: {
      not_in_record: {
        word: "Anyị enweghị ike ikwado ya",
        sentence: "Anyị achọtaghị nke a n'ndekọ anyị. Nke ahụ apụtaghị na ọ bụ ụgha.",
        instruction: "Lelee ọzọ mgbe e mesịrị, ma ọ bụ jụọ ụlọ ọrụ nke wepụtara ya.",
        action: "Lelee ọkwa ọzọ",
      },
      no_fact: {
        word: "Anyị enweghị ike ikwado ya",
        sentence: "Anyị ahụghị ihe ọ bụla n'ozi a anyị nwere ike ịlele na ndekọ.",
        instruction: "Tinye ọkwa ahụ n'onwe ya, ya na ụbọchị, ọnụọgụgụ ma ọ bụ njikọ ya.",
        action: "Lelee ọkwa ọzọ",
      },
      unclear: {
        word: "Anyị enweghị ike ikwado ya",
        sentence: "Anyị enweghị ike ịgụ nke a nke ọma iji doo anya.",
        instruction: "Zipụ mbipụta doro anya nke ọkwa ahụ.",
        action: "Zipụ foto doro anya",
      },
      line_missing: {
        word: "Anyị enweghị ike ikwado ya",
        sentence: "Ahịrị anyị chọrọ efunahụla n'mbipụta a.",
        instruction: "Zipụ ọkwa niile.",
        action: "Zipụ foto doro anya",
      },
    },
  },

  changes: {
    heading: "Ihe gbanwere",
    none: "Anyị ahụghị ihe dị iche n'akụkụ anyị nwere ike ịlele.",
    replace: "Mbipụta gị na-ekwu “{copy}”. Ọkwa gọọmentị na-ekwu “{official}”.",
    insert: "Mbipụta gị agbakwunyela “{copy}”. Ọkwa gọọmentị enweghị ya.",
    delete: "Mbipụta gị hapụrụ “{official}”.",
    conflict: "Mbipụta gị na-ekwu “{copy}”. Ọkwa gọọmentị na-ekwu “{official}”.",
    kinds: {
      date: "Ụbọchị",
      time: "Oge",
      weekday: "Ụbọchị izu",
      number: "Ọnụọgụgụ",
      money: "Ego",
      link: "Njikọ",
      phone: "Nọmba ekwentị",
      negation: "Ihe ọ pụtara",
      text: "Okwu",
    },
    conflictKinds: { date: "Ụbọchị", link: "Njikọ", money: "Ego" },
    replacedIntro:
      "Mbipụta gị dabara na ọkwa gọọmentị ochie okwu site n'okwu. Ọkwa ọhụrụ dị iche ebe a:",
    replacedNone: "Ọkwa ọhụrụ edochiela ya. Mepee ya ka ị hụ ihe dị iche.",
    to: "gaa",
    rowInsert: "Ọ nọ naanị n'ọkwa ochie: “{copy}”",
    rowDelete: "E gbakwunyere ya n'ọkwa ọhụrụ: “{official}”",
    now: "ugbu a",
  },

  receipt: {
    heading: "Akwụkwọ ihe akaebe",
    notice: "Ọkwa gọọmentị",
    noNotice: "Enweghị ọkwa gọọmentị dabara",
    published: "Ụbọchị e bipụtara",
    replacedBy: "E dochiela ya na",
    replacedByValue: "{id}, e bipụtara ya {date}",
    checked: "E lelere",
    recordAsOf: "Ndekọ ruo",
    code: "Koodu nlele",
    openOriginal: "Mepee ọkwa mbụ",
    viewSource: "Lee isi mmalite",
    verify: "Kwado nlele a",
  },

  share: {
    copied: "E detụrụ ya. Tinye ya n'mkparịta ụka.",
    copyFailed: "Enweghị ike idetu ya. Detụ adreesị ibe ahụ kama.",
    currentNoticeText: "Ọkwa nke ugbu a bụ {id}, e bipụtara ya {date}.",
    correctNoticeText: "Ọkwa ziri ezi: {title}",
  },
};
