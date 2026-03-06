/**
 * PSC Section 3 - Grammar Comparison Table
 * 語法對照表 - Common Cantonese/Hokkien grammar vs Standard Mandarin
 */

export interface GrammarItem {
  id: string;
  category: string;
  question: string;
  options: string[];
  correctAnswer: string;
  explanation: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

export const grammarTable: GrammarItem[] = [
  // Word order issues
  {
    id: "g1",
    category: "語序",
    question: "「我先走先」這個說法對嗎？",
    options: ["A. 對", "B. 不對，應該說「我先走」", "C. 不對，應該說「我走先」", "D. 不對，應該說「我先先去」"],
    correctAnswer: "B",
    explanation: "普通話的語序是「先...再...」，不說「...先」",
    difficulty: "medium"
  },
  {
    id: "g2",
    category: "語序",
    question: "「我好耐之前已經結婚」這個說法對嗎？",
    options: ["A. 對", "B. 不對，應該說「我很久以前已經結婚」", "C. 不對，應該說「我已經結婚很久」", "D. 不對，應該說「我結婚很久」"],
    correctAnswer: "B",
    explanation: "時間副詞「很久以前」修飾動詞，「已經」在動詞前",
    difficulty: "medium"
  },

  // Double comparatives
  {
    id: "g3",
    category: "比較句",
    question: "「我比他非常高」這個說法對嗎？",
    options: ["A. 對", "B. 不對，應該說「我比他高」", "C. 不對，應該說「我比他高很多」", "D. 不對，應該說「我比他較高」"],
    correctAnswer: "B",
    explanation: "比較句中不能同時用「比」和「非常/很」，只能選其一",
    difficulty: "easy"
  },
  {
    id: "g4",
    category: "比較句",
    question: "「這件衣服那件衣服貴」這個說法對嗎？",
    options: ["A. 對", "B. 不對，應該說「這件衣服比那件貴」", "C. 不對，應該說「這件衣服貴過那件」", "D. 不對，應該說「這件衣服比較貴」"],
    correctAnswer: "B",
    explanation: "普通話比較句用「比」字結構",
    difficulty: "easy"
  },

  // Aspect particles
  {
    id: "g5",
    category: "動態助詞",
    question: "「我食緊飯」應該怎麼說？",
    options: ["A. 我吃飯", "B. 我正在吃飯", "C. 我吃著飯", "D. 我吃過飯"],
    correctAnswer: "B",
    explanation: "「食緊」表示動作進行中，普通話用「正在」或「在」",
    difficulty: "medium"
  },
  {
    id: "g6",
    category: "動態助詞",
    question: "「我已經食咗飯」應該怎麼說？",
    options: ["A. 我吃飯了", "B. 我吃過飯", "C. 我吃著飯", "D. 我吃了飯"],
    correctAnswer: "A",
    explanation: "「食咗」表示已完成，用「了」表示",
    difficulty: "medium"
  },
  {
    id: "g7",
    category: "動態助詞",
    question: "「佢去咗美國」應該怎麼說？",
    options: ["A. 他去美國", "B. 他去了美國", "C. 他去過美國", "D. 他正去美國"],
    correctAnswer: "B",
    explanation: "「咗」表示完成，相當於普通話的「了」",
    difficulty: "medium"
  },

  // Negation
  {
    id: "g8",
    category: "否定詞",
    question: "「我唔知」應該怎麼說？",
    options: ["A. 我不知", "B. 我不知道", "C. 我不曉得", "D. 我沒知道"],
    correctAnswer: "B",
    explanation: "「唔知」在普通話中說「不知道」",
    difficulty: "easy"
  },
  {
    id: "g9",
    category: "否定詞",
    question: "「我有去」應該怎麼說？",
    options: ["A. 我不去", "B. 我沒去", "C. 我不去過", "D. 我不去了"],
    correctAnswer: "B",
    explanation: "「有」表示完成/經歷，相當於普通話的「了」或「過」",
    difficulty: "medium"
  },
  {
    id: "g10",
    category: "否定詞",
    question: "「你晤應該咁樣做」應該怎麼說？",
    options: ["A. 你不應該這樣做", "B. 你不該這樣做", "C.你不應該這樣做", "D. 兩者都可"],
    correctAnswer: "D",
    explanation: "「應該」和「該」在普通話中都可以表示義務",
    difficulty: "medium"
  },

  // Question particles
  {
    id: "g11",
    category: "疑問句",
    question: "「你食咗未？」應該怎麼說？",
    options: ["A. 你吃了沒有？", "B. 你吃了嗎？", "C. 你吃了没？", "D. 兩者都可"],
    correctAnswer: "D",
    explanation: "「未」相當於普通話的「了沒有」或「了嗎」",
    difficulty: "easy"
  },
  {
    id: "g12",
    category: "疑問句",
    question: "「你係唔係香港人？」應該怎麼說？",
    options: ["A. 你是香港人？", "B. 你是香港人嗎？", "C. 你是不是香港人？", "D. 三者都可"],
    correctAnswer: "D",
    explanation: "普通話有多種提問方式，都正確",
    difficulty: "easy"
  },

  // Ba sentence
  {
    id: "g13",
    category: "把字句",
    question: "「我將本書放係枱面」應該怎麼說？",
    options: ["A. 我把書放在桌面", "B. 我把書放桌面", "C. 我書放桌面", "D. 兩者都可"],
    correctAnswer: "A",
    explanation: "「把」字句要完整，介詞「在」不能省略",
    difficulty: "medium"
  },
  {
    id: "g14",
    category: "把字句",
    question: "「你弊咗啦！」應該怎麼說？",
    options: ["A. 你壞了！", "B. 你把事情搞砸了！", "C. 你完了！", "D. 你不行！"],
    correctAnswer: "B",
    explanation: "「弊」在粵語中表示搞砸了，普通話用「把...搞砸」",
    difficulty: "hard"
  },

  // Passive voice
  {
    id: "g15",
    category: "被字句",
    question: "「隻杯俾佢整爛咗」應該怎麼說？",
    options: ["A. 杯子給他打破了", "B. 杯子被他打破了", "C. 杯子他打破了", "D. 兩者都可"],
    correctAnswer: "B",
    explanation: "被字句表示被動，用「被」引進動作主動者",
    difficulty: "medium"
  },
  {
    id: "g16",
    category: "被字句",
    question: "「封信俾風吹走咗」應該怎麼說？",
    options: ["A. 信被風吹走了", "B. 信給風吹走了", "C. 風把信吹走了", "D. 三者都可"],
    correctAnswer: "D",
    explanation: "被字句、把字句、主動句可以互換",
    difficulty: "hard"
  },

  // Tense/Time
  {
    id: "g17",
    category: "時間表達",
    question: "「聽日」應該怎麼說？",
    options: ["A. 今天", "B. 明天", "C. 後天", "D. 昨天"],
    correctAnswer: "B",
    explanation: "「聽日」是粵語，明天普通話說「明天」",
    difficulty: "easy"
  },
  {
    id: "g18",
    category: "時間表達",
    question: "「琴日」應該怎麼說？",
    options: ["A. 今天", "B. 明天", "C. 後天", "D. 昨天"],
    correctAnswer: "D",
    explanation: "「琴日」是粵語，昨天普通話說「昨天」",
    difficulty: "easy"
  },
  {
    id: "g19",
    category: "時間表達",
    question: "「尋晚」應該怎麼說？",
    options: ["A. 昨晚", "B. 昨晚", "C. 昨天夜裡", "D. 兩者都可"],
    correctAnswer: "D",
    explanation: "「尋晚」普通話說「昨晚」或「昨天夜裡」",
    difficulty: "easy"
  },
  {
    id: "g20",
    category: "時間表達",
    question: "「”而家」應該怎麼說？",
    options: ["A. 現在", "B. 這會兒", "C. 這時候", "D. 兩者都可"],
    correctAnswer: "D",
    explanation: "「而家」是粵語/客語，普通話說「現在」",
    difficulty: "easy"
  },
];

export default grammarTable;
