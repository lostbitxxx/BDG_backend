/**
 * PSC Section 3 - Classifier (Measure Word) & Noun Collocations
 * 量詞名詞搭配表
 */

export interface ClassifierItem {
  id: string;
  noun: string;
  nounPinyin: string;
  classifier: string;
  classifierPinyin: string;
  notes?: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

export const classifierTable: ClassifierItem[] = [
  // Books/Papers
  { id: "c1", noun: "書", nounPinyin: "shū", classifier: "本", classifierPinyin: "běn", difficulty: "easy" },
  { id: "c2", noun: "雜誌", nounPinyin: "zázhì", classifier: "本", classifierPinyin: "běn", difficulty: "easy" },
  { id: "c3", noun: "報紙", nounPinyin: "bàozhǐ", classifier: "張", classifierPinyin: "zhāng", difficulty: "easy" },
  { id: "c4", noun: "信", nounPinyin: "xìn", classifier: "封", classifierPinyin: "fēng", difficulty: "easy" },

  // People/Animals
  { id: "c5", noun: "人", nounPinyin: "rén", classifier: "個", classifierPinyin: "gè", difficulty: "easy" },
  { id: "c6", noun: "牛", nounPinyin: "niú", classifier: "頭", classifierPinyin: "tóu", difficulty: "easy" },
  { id: "c7", noun: "馬", nounPinyin: "mǎ", classifier: "匹", classifierPinyin: "pǐ", difficulty: "easy" },
  { id: "c8", noun: "羊", nounPinyin: "yáng", classifier: "隻", classifierPinyin: "zhī", difficulty: "easy" },
  { id: "c9", noun: "魚", nounPinyin: "yú", classifier: "條", classifierPinyin: "tiáo", difficulty: "easy" },
  { id: "c10", noun: "狗", nounPinyin: "gǒu", classifier: "隻", classifierPinyin: "zhī", difficulty: "easy" },
  { id: "c11", noun: "貓", nounPinyin: "māo", classifier: "隻", classifierPinyin: "zhī", difficulty: "easy" },
  { id: "c12", noun: "鳥", nounPinyin: "niǎo", classifier: "隻", classifierPinyin: "zhī", difficulty: "easy" },
  { id: "c13", noun: "蟲", nounPinyin: "chóng", classifier: "條", classifierPinyin: "tiáo", difficulty: "medium" },

  // Vehicles
  { id: "c14", noun: "飛機", nounPinyin: "fēijī", classifier: "架", classifierPinyin: "jià", difficulty: "easy" },
  { id: "c15", noun: "火車", nounPinyin: "huǒchē", classifier: "列", classifierPinyin: "liè", difficulty: "easy" },
  { id: "c16", noun: "汽車", nounPinyin: "qìchē", classifier: "輛", classifierPinyin: "liàng", difficulty: "easy" },
  { id: "c17", noun: "自行車", nounPinyin: "zìxíngchē", classifier: "輛", classifierPinyin: "liàng", difficulty: "easy" },
  { id: "c18", noun: "船", nounPinyin: "chuán", classifier: "艘", classifierPinyin: "sōu", difficulty: "medium" },

  // Buildings/Structures
  { id: "c19", noun: "房子", nounPinyin: "fángzi", classifier: "幢", classifierPinyin: "zhuàng", difficulty: "easy" },
  { id: "c20", noun: "樓", nounPinyin: "lóu", classifier: "層", classifierPinyin: "céng", difficulty: "easy" },
  { id: "c21", noun: "橋", nounPinyin: "qiáo", classifier: "座", classifierPinyin: "zuò", difficulty: "easy" },
  { id: "c22", noun: "塔", nounPinyin: "tǎ", classifier: "座", classifierPinyin: "zuò", difficulty: "easy" },

  // Utensils/Items
  { id: "c23", noun: "傘", nounPinyin: "sǎn", classifier: "把", classifierPinyin: "bǎ", difficulty: "easy" },
  { id: "c24", noun: "刀", nounPinyin: "dāo", classifier: "把", classifierPinyin: "bǎ", difficulty: "easy" },
  { id: "c25", noun: "梳子", nounPinyin: "shūzi", classifier: "把", classifierPinyin: "bǎ", difficulty: "easy" },
  { id: "c26", noun: "椅子", nounPinyin: "yǐzi", classifier: "把", classifierPinyin: "bǎ", difficulty: "easy" },
  { id: "c27", noun: "鎖", nounPinyin: "suǒ", classifier: "把", classifierPinyin: "bǎ", difficulty: "easy" },
  { id: "c28", noun: "鑰匙", nounPinyin: "yàoshi", classifier: "把", classifierPinyin: "bǎ", difficulty: "easy" },

  // Clothing
  { id: "c29", noun: "衣服", nounPinyin: "yīfu", classifier: "件", classifierPinyin: "jiàn", difficulty: "easy" },
  { id: "c30", noun: "裙子", nounPinyin: "qúnzi", classifier: "條", classifierPinyin: "tiáo", difficulty: "easy" },
  { id: "c31", noun: "褲子", nounPinyin: "kùzi", classifier: "條", classifierPinyin: "tiáo", difficulty: "easy" },
  { id: "c32", noun: "襪子", nounPinyin: "wàzi", classifier: "雙", classifierPinyin: "shuāng", difficulty: "easy" },
  { id: "c33", noun: "鞋", nounPinyin: "xié", classifier: "雙", classifierPinyin: "shuāng", difficulty: "easy" },

  // Food
  { id: "c34", noun: "米", nounPinyin: "mǐ", classifier: "粒", classifierPinyin: "lì", difficulty: "easy" },
  { id: "c35", noun: "飯", nounPinyin: "fàn", classifier: "碗", classifierPinyin: "wǎn", difficulty: "easy" },
  { id: "c36", noun: "麵", nounPinyin: "miàn", classifier: "碗", classifierPinyin: "wǎn", difficulty: "easy" },
  { id: "c37", noun: "包子", nounPinyin: "bāozi", classifier: "個", classifierPinyin: "gè", difficulty: "easy" },
  { id: "c38", noun: "饅頭", nounPinyin: "mántou", classifier: "個", classifierPinyin: "gè", difficulty: "easy" },
  { id: "c39", noun: "蘋果", nounPinyin: "píngguǒ", classifier: "個", classifierPinyin: "gè", difficulty: "easy" },
  { id: "c40", noun: "橘子", nounPinyin: "júzi", classifier: "個", classifierPinyin: "gè", difficulty: "easy" },

  // Abstract items
  { id: "c41", noun: "事", nounPinyin: "shì", classifier: "件", classifierPinyin: "jiàn", difficulty: "easy" },
  { id: "c42", noun: "工作", nounPinyin: "gōngzuò", classifier: "份", classifierPinyin: "fèn", difficulty: "easy" },
  { id: "c43", noun: "禮物", nounPinyin: "lǐwù", classifier: "份", classifierPinyin: "fèn", difficulty: "easy" },
  { id: "c44", noun: "報紙", nounPinyin: "bàozhǐ", classifier: "份", classifierPinyin: "fèn", difficulty: "easy" },

  // Difficult ones (common mistakes)
  { id: "c45", noun: "公共汽車", nounPinyin: "gōnggòng qìchē", classifier: "輛", classifierPinyin: "liàng", notes: "不是「部」", difficulty: "hard" },
  { id: "c46", noun: "出租車", nounPinyin: "chūzū chē", classifier: "輛", classifierPinyin: "liàng", notes: "不是「部」或「架」", difficulty: "hard" },
  { id: "c47", noun: "交通事故", nounPinyin: "jiāotōng shìgù", classifier: "起", classifierPinyin: "qǐ", difficulty: "medium" },
  { id: "c48", noun: "案件", nounPinyin: "ànjiàn", classifier: "起", classifierPinyin: "qǐ", difficulty: "medium" },
  { id: "c49", noun: "錯誤", nounPinyin: "cuòwù", classifier: "個", classifierPinyin: "gè", difficulty: "medium" },
  { id: "c50", noun: "問題", nounPinyin: "wèntí", classifier: "個", classifierPinyin: "gè", difficulty: "easy" },
];

export default classifierTable;
