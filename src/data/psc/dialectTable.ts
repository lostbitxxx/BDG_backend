/**
 * PSC Section 3 - Dialect Vocabulary Comparison Table
 * 方言對照表 - Common dialect words vs Standard Mandarin
 */

export interface DialectItem {
  id: string;
  category: string;
  standard: string;      // 普通话规范说法
  pinyin: string;
  dialects: {
    [key: string]: string;  // dialect name -> word
  };
  difficulty: 'easy' | 'medium' | 'hard';
}

export const dialectTable: DialectItem[] = [
  // Pronouns
  {
    id: "d1",
    category: "人稱代詞",
    standard: "我們",
    pinyin: "wǒmen",
    dialects: {
      cantonese: "我哋",
      hokkien: "阮",
      taiwan: "我們"
    },
    difficulty: "easy"
  },
  {
    id: "d2",
    category: "人稱代詞",
    standard: "他們",
    pinyin: "tāmen",
    dialects: {
      cantonese: "佢哋",
      hokkien: "怹",
      taiwan: "他們"
    },
    difficulty: "easy"
  },
  {
    id: "d3",
    category: "人稱代詞",
    standard: "什麼",
    pinyin: "shénme",
    dialects: {
      cantonese: "咩",
      hokkien: "啥",
      taiwan: "什麼"
    },
    difficulty: "easy"
  },

  // Daily items
  {
    id: "d4",
    category: "日常用品",
    standard: "自行車",
    pinyin: "zìxíngchē",
    dialects: {
      cantonese: "單車",
      hokkien: "腳踏車",
      taiwan: "腳踏車"
    },
    difficulty: "easy"
  },
  {
    id: "d5",
    category: "日常用品",
    standard: "土豆",
    pinyin: "tǔdòu",
    dialects: {
      cantonese: "薯仔",
      hokkien: "花生",
      taiwan: "土豆"
    },
    difficulty: "medium"
  },
  {
    id: "d6",
    category: "日常用品",
    standard: "雞蛋",
    pinyin: "jīdàn",
    dialects: {
      cantonese: "雞蛋",
      hokkien: "雞卵",
      taiwan: "蛋"
    },
    difficulty: "easy"
  },
  {
    id: "d7",
    category: "日常用品",
    standard: "便宜",
    pinyin: "piányi",
    dialects: {
      cantonese: "平",
      hokkien: "俗",
      taiwan: "便宜"
    },
    difficulty: "easy"
  },

  // Food
  {
    id: "d8",
    category: "食物",
    standard: "饅頭",
    pinyin: "mántou",
    dialects: {
      cantonese: "包",
      hokkien: "饅頭",
      taiwan: "饅頭"
    },
    difficulty: "medium"
  },
  {
    id: "d9",
    category: "食物",
    standard: "稀飯",
    pinyin: "xīfàn",
    dialects: {
      cantonese: "粥",
      hokkien: "糜",
      taiwan: "稀飯"
    },
    difficulty: "easy"
  },
  {
    id: "d10",
    category: "食物",
    standard: "菠菜",
    pinyin: "bōcài",
    dialects: {
      cantonese: "菠菜",
      hokkien: "飛龍",
      taiwan: "菠菜"
    },
    difficulty: "hard"
  },

  // Verbs
  {
    id: "d11",
    category: "動詞",
    standard: "不知道",
    pinyin: "bù zhīdào",
    dialects: {
      cantonese: "唔知",
      hokkien: "袂知",
      taiwan: "不知道"
    },
    difficulty: "easy"
  },
  {
    id: "d12",
    category: "動詞",
    standard: "吃",
    pinyin: "chī",
    dialects: {
      cantonese: "食",
      hokkien: "食",
      taiwan: "吃"
    },
    difficulty: "easy"
  },
  {
    id: "d13",
    category: "動詞",
    standard: "喝",
    pinyin: "hē",
    dialects: {
      cantonese: "飲",
      hokkien: "啉",
      taiwan: "喝"
    },
    difficulty: "easy"
  },
  {
    id: "d14",
    category: "動詞",
    standard: "玩",
    pinyin: "wán",
    dialects: {
      cantonese: "玩",
      hokkien: "耍",
      taiwan: "玩"
    },
    difficulty: "easy"
  },
  {
    id: "d15",
    category: "動詞",
    standard: "給",
    pinyin: "gěi",
    dialects: {
      cantonese: "畀",
      hokkien: "互",
      taiwan: "給"
    },
    difficulty: "medium"
  },

  // Adjectives
  {
    id: "d16",
    category: "形容詞",
    standard: "很多",
    pinyin: "hěn duō",
    dialects: {
      cantonese: "好多",
      hokkien: "誠多",
      taiwan: "很多"
    },
    difficulty: "easy"
  },
  {
    id: "d17",
    category: "形容詞",
    standard: "漂亮",
    pinyin: "piàoliang",
    dialects: {
      cantonese: "靚",
      hokkien: "水",
      taiwan: "漂亮"
    },
    difficulty: "easy"
  },
  {
    id: "d18",
    category: "形容詞",
    standard: "能幹",
    pinyin: "nénggàn",
    dialects: {
      cantonese: "醒",
      hokkien: "骨力",
      taiwan: "能幹"
    },
    difficulty: "hard"
  },
  {
    id: "d19",
    category: "形容詞",
    standard: "愚蠢",
    pinyin: "yúchǔn",
    dialects: {
      cantonese: "蠢",
      hokkien: "戇",
      taiwan: "笨"
    },
    difficulty: "medium"
  },
  {
    id: "d20",
    category: "形容詞",
    standard: "害怕",
    pinyin: "hàipà",
    dialects: {
      cantonese: "驚",
      hokkien: "驚",
      taiwan: "怕"
    },
    difficulty: "easy"
  },
];

export default dialectTable;
