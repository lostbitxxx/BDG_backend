/**
 * PSC Question Bank - For backend use
 * Shared question data for test generation
 */

export interface Question {
  id: string;
  section: 1 | 2 | 3 | 4 | 5;
  type: 'reading' | 'listening' | 'choice' | 'speaking';
  content: string;
  pinyin?: string;
  audioUrl?: string;
  options?: string[];
  correctAnswer?: string;
  tags?: string[]; // For filtering: tone_1, tone_2, retroflex, n_vs_l, etc.
}

// Section 1: Single character reading
export const section1Questions: Question[] = [
  // Tone 1
  { id: 's1-1', section: 1, type: 'reading', content: '八', pinyin: 'bā', tags: ['tone_1'] },
  { id: 's1-2', section: 1, type: 'reading', content: '七', pinyin: 'qī', tags: ['tone_1'] },
  { id: 's1-3', section: 1, type: 'reading', content: '六', pinyin: 'liù', tags: ['tone_4'] },
  { id: 's1-4', section: 1, type: 'reading', content: '五', pinyin: 'wǔ', tags: ['tone_3'] },
  { id: 's1-5', section: 1, type: 'reading', content: '四', pinyin: 'sì', tags: ['tone_4'] },
  { id: 's1-6', section: 1, type: 'reading', content: '三', pinyin: 'sān', tags: ['tone_1'] },
  { id: 's1-7', section: 1, type: 'reading', content: '二', pinyin: 'èr', tags: ['tone_4'] },
  { id: 's1-8', section: 1, type: 'reading', content: '一', pinyin: 'yī', tags: ['tone_1'] },
  { id: 's1-9', section: 1, type: 'reading', content: '九', pinyin: 'jiǔ', tags: ['tone_3'] },
  { id: 's1-10', section: 1, type: 'reading', content: '十', pinyin: 'shí', tags: ['tone_2'] },
  // Retroflex (zh/ch/sh)
  { id: 's1-11', section: 1, type: 'reading', content: '中', pinyin: 'zhōng', tags: ['retroflex', 'tone_1'] },
  { id: 's1-12', section: 1, type: 'reading', content: '是', pinyin: 'shì', tags: ['retroflex', 'tone_4'] },
  { id: 's1-13', section: 1, type: 'reading', content: '时', pinyin: 'shí', tags: ['retroflex', 'tone_2'] },
  { id: 's1-14', section: 1, type: 'reading', content: '事', pinyin: 'shì', tags: ['retroflex', 'tone_4'] },
  { id: 's1-15', section: 1, type: 'reading', content: '出', pinyin: 'chū', tags: ['retroflex', 'tone_1'] },
  { id: 's1-16', section: 1, type: 'reading', content: '吃', pinyin: 'chī', tags: ['retroflex', 'tone_1'] },
  { id: 's1-17', section: 1, type: 'reading', content: '车', pinyin: 'chē', tags: ['retroflex', 'tone_1'] },
  { id: 's1-18', section: 1, type: 'reading', content: '书', pinyin: 'shū', tags: ['retroflex', 'tone_1'] },
  { id: 's1-19', section: 1, type: 'reading', content: '树', pinyin: 'shù', tags: ['retroflex', 'tone_4'] },
  { id: 's1-20', section: 1, type: 'reading', content: '知', pinyin: 'zhī', tags: ['retroflex', 'tone_1'] },
  // n vs l
  { id: 's1-21', section: 1, type: 'reading', content: '南', pinyin: 'nán', tags: ['n_vs_l', 'tone_2'] },
  { id: 's1-22', section: 1, type: 'reading', content: '兰', pinyin: 'lán', tags: ['n_vs_l', 'tone_2'] },
  { id: 's1-23', section: 1, type: 'reading', content: '年', pinyin: 'nián', tags: ['n_vs_l', 'tone_2'] },
  { id: 's1-24', section: 1, type: 'reading', content: '连', pinyin: 'lián', tags: ['n_vs_l', 'tone_2'] },
  { id: 's1-25', section: 1, type: 'reading', content: '女', pinyin: 'nǚ', tags: ['n_vs_l', 'tone_3'] },
  { id: 's1-26', section: 1, type: 'reading', content: '绿', pinyin: 'lǜ', tags: ['n_vs_l', 'tone_4'] },
  { id: 's1-27', section: 1, type: 'reading', content: '怒', pinyin: 'nù', tags: ['n_vs_l', 'tone_4'] },
  { id: 's1-28', section: 1, type: 'reading', content: '路', pinyin: 'lù', tags: ['n_vs_l', 'tone_4'] },
  { id: 's1-29', section: 1, type: 'reading', content: '脑', pinyin: 'nǎo', tags: ['n_vs_l', 'tone_3'] },
  { id: 's1-30', section: 1, type: 'reading', content: '老', pinyin: 'lǎo', tags: ['n_vs_l', 'tone_3'] },
  // f vs h
  { id: 's1-31', section: 1, type: 'reading', content: '飞', pinyin: 'fēi', tags: ['f_vs_h', 'tone_1'] },
  { id: 's1-32', section: 1, type: 'reading', content: '灰', pinyin: 'huī', tags: ['f_vs_h', 'tone_1'] },
  { id: 's1-33', section: 1, type: 'reading', content: '发', pinyin: 'fā', tags: ['f_vs_h', 'tone_1'] },
  { id: 's1-34', section: 1, type: 'reading', content: '花', pinyin: 'huā', tags: ['f_vs_h', 'tone_1'] },
  { id: 's1-35', section: 1, type: 'reading', content: '分', pinyin: 'fēn', tags: ['f_vs_h', 'tone_1'] },
  { id: 's1-36', section: 1, type: 'reading', content: '昏', pinyin: 'hūn', tags: ['f_vs_h', 'tone_1'] },
  // Common
  { id: 's1-37', section: 1, type: 'reading', content: '我', pinyin: 'wǒ', tags: ['tone_3'] },
  { id: 's1-38', section: 1, type: 'reading', content: '你', pinyin: 'nǐ', tags: ['tone_3'] },
  { id: 's1-39', section: 1, type: 'reading', content: '他', pinyin: 'tā', tags: ['tone_1'] },
  { id: 's1-40', section: 1, type: 'reading', content: '人', pinyin: 'rén', tags: ['tone_2'] },
  { id: 's1-41', section: 1, type: 'reading', content: '大', pinyin: 'dà', tags: ['tone_4'] },
  { id: 's1-42', section: 1, type: 'reading', content: '小', pinyin: 'xiǎo', tags: ['tone_3'] },
  { id: 's1-43', section: 1, type: 'reading', content: '好', pinyin: 'hǎo', tags: ['tone_3'] },
  { id: 's1-44', section: 1, type: 'reading', content: '看', pinyin: 'kàn', tags: ['tone_4'] },
  { id: 's1-45', section: 1, type: 'reading', content: '来', pinyin: 'lái', tags: ['tone_2'] },
  { id: 's1-46', section: 1, type: 'reading', content: '去', pinyin: 'qù', tags: ['tone_4'] },
  { id: 's1-47', section: 1, type: 'reading', content: '有', pinyin: 'yǒu', tags: ['tone_3'] },
  { id: 's1-48', section: 1, type: 'reading', content: '没', pinyin: 'méi', tags: ['tone_2'] },
  { id: 's1-49', section: 1, type: 'reading', content: '这', pinyin: 'zhè', tags: ['retroflex', 'tone_4'] },
  { id: 's1-50', section: 1, type: 'reading', content: '那', pinyin: 'nà', tags: ['tone_4'] },
  // More tones
  { id: 's1-51', section: 1, type: 'reading', content: '妈', pinyin: 'mā', tags: ['tone_1'] },
  { id: 's1-52', section: 1, type: 'reading', content: '马', pinyin: 'mǎ', tags: ['tone_3'] },
  { id: 's1-53', section: 1, type: 'reading', content: '骂', pinyin: 'mà', tags: ['tone_4'] },
  { id: 's1-54', section: 1, type: 'reading', content: '爸', pinyin: 'bà', tags: ['tone_4'] },
  { id: 's1-55', section: 1, type: 'reading', content: '杯', pinyin: 'bēi', tags: ['tone_1'] },
  { id: 's1-56', section: 1, type: 'reading', content: '背', pinyin: 'bēi', tags: ['tone_1'] },
  { id: 's1-57', section: 1, type: 'reading', content: '被', pinyin: 'bèi', tags: ['tone_4'] },
  { id: 's1-58', section: 1, type: 'reading', content: '报', pinyin: 'bào', tags: ['tone_4'] },
  { id: 's1-59', section: 1, type: 'reading', content: '包', pinyin: 'bāo', tags: ['tone_1'] },
  { id: 's1-60', section: 1, type: 'reading', content: '饱', pinyin: 'bǎo', tags: ['tone_3'] },
  { id: 's1-61', section: 1, type: 'reading', content: '抱', pinyin: 'bào', tags: ['tone_4'] },
  { id: 's1-62', section: 1, type: 'reading', content: '跑', pinyin: 'pǎo', tags: ['tone_3'] },
  { id: 's1-63', section: 1, type: 'reading', content: '怕', pinyin: 'pà', tags: ['tone_4'] },
  { id: 's1-64', section: 1, type: 'reading', content: '拿', pinyin: 'ná', tags: ['tone_2'] },
  { id: 's1-65', section: 1, type: 'reading', content: '哪', pinyin: 'nǎ', tags: ['tone_3'] },
  { id: 's1-66', section: 1, type: 'reading', content: '家', pinyin: 'jiā', tags: ['tone_1'] },
  { id: 's1-67', section: 1, type: 'reading', content: '假', pinyin: 'jiǎ', tags: ['tone_3'] },
  { id: 's1-68', section: 1, type: 'reading', content: '价', pinyin: 'jià', tags: ['tone_4'] },
  { id: 's1-69', section: 1, type: 'reading', content: '加', pinyin: 'jiā', tags: ['tone_1'] },
  { id: 's1-70', section: 1, type: 'reading', content: '夹', pinyin: 'jiá', tags: ['tone_2'] },
  { id: 's1-71', section: 1, type: 'reading', content: '教', pinyin: 'jiāo', tags: ['tone_1'] },
  { id: 's1-72', section: 1, type: 'reading', content: '交', pinyin: 'jiāo', tags: ['tone_1'] },
  { id: 's1-73', section: 1, type: 'reading', content: '叫', pinyin: 'jiào', tags: ['tone_4'] },
  { id: 's1-74', section: 1, type: 'reading', content: '觉', pinyin: 'jué', tags: ['tone_2'] },
  { id: 's1-75', section: 1, type: 'reading', content: '绝', pinyin: 'jué', tags: ['tone_2'] },
  { id: 's1-76', section: 1, type: 'reading', content: '酒', pinyin: 'jiǔ', tags: ['tone_3'] },
  { id: 's1-77', section: 1, type: 'reading', content: '就', pinyin: 'jiù', tags: ['tone_4'] },
  { id: 's1-78', section: 1, type: 'reading', content: '九', pinyin: 'jiǔ', tags: ['tone_3'] },
  // More n vs l
  { id: 's1-79', section: 1, type: 'reading', content: '农', pinyin: 'nóng', tags: ['n_vs_l', 'tone_2'] },
  { id: 's1-80', section: 1, type: 'reading', content: '龙', pinyin: 'lóng', tags: ['n_vs_l', 'tone_2'] },
  { id: 's1-81', section: 1, type: 'reading', content: '暖', pinyin: 'nuǎn', tags: ['n_vs_l', 'tone_3'] },
  { id: 's1-82', section: 1, type: 'reading', content: '卵', pinyin: 'luǎn', tags: ['n_vs_l', 'tone_3'] },
  { id: 's1-83', section: 1, type: 'reading', content: '林', pinyin: 'lín', tags: ['n_vs_l', 'tone_2'] },
  { id: 's1-84', section: 1, type: 'reading', content: '您', pinyin: 'nín', tags: ['tone_2'] },
  { id: 's1-85', section: 1, type: 'reading', content: '令', pinyin: 'lìng', tags: ['n_vs_l', 'tone_4'] },
  // More f vs h
  { id: 's1-86', section: 1, type: 'reading', content: '方', pinyin: 'fāng', tags: ['f_vs_h', 'tone_1'] },
  { id: 's1-87', section: 1, type: 'reading', content: '黄', pinyin: 'huáng', tags: ['f_vs_h', 'tone_2'] },
  { id: 's1-88', section: 1, type: 'reading', content: '风', pinyin: 'fēng', tags: ['f_vs_h', 'tone_1'] },
  { id: 's1-89', section: 1, type: 'reading', content: '红', pinyin: 'hóng', tags: ['f_vs_h', 'tone_2'] },
  { id: 's1-90', section: 1, type: 'reading', content: '冯', pinyin: 'féng', tags: ['f_vs_h', 'tone_2'] },
  // More retroflex
  { id: 's1-91', section: 1, type: 'reading', content: '张', pinyin: 'zhāng', tags: ['retroflex', 'tone_1'] },
  { id: 's1-92', section: 1, type: 'reading', content: '常', pinyin: 'cháng', tags: ['retroflex', 'tone_2'] },
  { id: 's1-93', section: 1, type: 'reading', content: '长', pinyin: 'cháng', tags: ['retroflex', 'tone_2'] },
  { id: 's1-94', section: 1, type: 'reading', content: '上', pinyin: 'shàng', tags: ['retroflex', 'tone_4'] },
  { id: 's1-95', section: 1, type: 'reading', content: '山', pinyin: 'shān', tags: ['retroflex', 'tone_1'] },
  { id: 's1-96', section: 1, type: 'reading', content: '水', pinyin: 'shuǐ', tags: ['retroflex', 'tone_3'] },
  { id: 's1-97', section: 1, type: 'reading', content: '睡', pinyin: 'shuì', tags: ['retroflex', 'tone_4'] },
  { id: 's1-98', section: 1, type: 'reading', content: '说', pinyin: 'shuō', tags: ['retroflex', 'tone_1'] },
  { id: 's1-99', section: 1, type: 'reading', content: '顺', pinyin: 'shùn', tags: ['retroflex', 'tone_4'] },
  { id: 's1-100', section: 1, type: 'reading', content: '春', pinyin: 'chūn', tags: ['retroflex', 'tone_1'] },
  { id: 's1-101', section: 1, type: 'reading', content: '纯', pinyin: 'chún', tags: ['retroflex', 'tone_2'] },
  { id: 's1-102', section: 1, type: 'reading', content: '庄', pinyin: 'zhuāng', tags: ['retroflex', 'tone_1'] },
  { id: 's1-103', section: 1, type: 'reading', content: '装', pinyin: 'zhuāng', tags: ['retroflex', 'tone_1'] },
  { id: 's1-104', section: 1, type: 'reading', content: '壮', pinyin: 'zhuàng', tags: ['retroflex', 'tone_4'] },

  // z/c/s vs zh/ch/sh (flat initials - difficult for Cantonese speakers)
  { id: 's1-z1', section: 1, type: 'reading', content: '子', pinyin: 'zǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-z2', section: 1, type: 'reading', content: '字', pinyin: 'zì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-z3', section: 1, type: 'reading', content: '走', pinyin: 'zǒu', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-z4', section: 1, type: 'reading', content: '早', pinyin: 'zǎo', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-z5', section: 1, type: 'reading', content: '在', pinyin: 'zài', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-z6', section: 1, type: 'reading', content: '作', pinyin: 'zuò', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-z7', section: 1, type: 'reading', content: '坐', pinyin: 'zuò', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-z8', section: 1, type: 'reading', content: '租', pinyin: 'zū', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-z9', section: 1, type: 'reading', content: '足', pinyin: 'zú', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-z10', section: 1, type: 'reading', content: '增', pinyin: 'zēng', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-z11', section: 1, type: 'reading', content: '赠', pinyin: 'zèng', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-z12', section: 1, type: 'reading', content: '宗', pinyin: 'zōng', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-z13', section: 1, type: 'reading', content: '嘴', pinyin: 'zuǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-z14', section: 1, type: 'reading', content: '造', pinyin: 'zào', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-z15', section: 1, type: 'reading', content: '砸', pinyin: 'zá', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-z16', section: 1, type: 'reading', content: '阻', pinyin: 'zǔ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-z17', section: 1, type: 'reading', content: '昨', pinyin: 'zuó', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-z18', section: 1, type: 'reading', content: '仔', pinyin: 'zǎi', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  // c:
  { id: 's1-c1', section: 1, type: 'reading', content: '次', pinyin: 'cì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-c2', section: 1, type: 'reading', content: '雌', pinyin: 'cí', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-c3', section: 1, type: 'reading', content: '此', pinyin: 'cǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-c4', section: 1, type: 'reading', content: '粗', pinyin: 'cū', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-c5', section: 1, type: 'reading', content: '错', pinyin: 'cuò', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-c6', section: 1, type: 'reading', content: '存', pinyin: 'cún', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-c7', section: 1, type: 'reading', content: '从', pinyin: 'cóng', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-c8', section: 1, type: 'reading', content: '参', pinyin: 'cān', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-c9', section: 1, type: 'reading', content: '彩', pinyin: 'cǎi', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-c10', section: 1, type: 'reading', content: '才', pinyin: 'cái', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-c11', section: 1, type: 'reading', content: '菜', pinyin: 'cài', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-c12', section: 1, type: 'reading', content: '采', pinyin: 'cǎi', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-c13', section: 1, type: 'reading', content: '餐', pinyin: 'cān', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-c14', section: 1, type: 'reading', content: '醋', pinyin: 'cù', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-c15', section: 1, type: 'reading', content: '促', pinyin: 'cù', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-c16', section: 1, type: 'reading', content: '村', pinyin: 'cūn', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  // s:
  { id: 's1-s1', section: 1, type: 'reading', content: '四', pinyin: 'sì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s2', section: 1, type: 'reading', content: '死', pinyin: 'sǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-s3', section: 1, type: 'reading', content: '司', pinyin: 'sī', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-s4', section: 1, type: 'reading', content: '思', pinyin: 'sī', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-s5', section: 1, type: 'reading', content: '送', pinyin: 'sòng', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s6', section: 1, type: 'reading', content: '算', pinyin: 'suàn', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s7', section: 1, type: 'reading', content: '色', pinyin: 'sè', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s8', section: 1, type: 'reading', content: '岁', pinyin: 'suì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s9', section: 1, type: 'reading', content: '寺', pinyin: 'sì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s10', section: 1, type: 'reading', content: '散', pinyin: 'sàn', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s11', section: 1, type: 'reading', content: '速', pinyin: 'sù', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s12', section: 1, type: 'reading', content: '塑', pinyin: 'sù', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-s13', section: 1, type: 'reading', content: '搜', pinyin: 'sōu', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-s14', section: 1, type: 'reading', content: '宿', pinyin: 'sù', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  // zh (for comparison)
  { id: 's1-zh1', section: 1, type: 'reading', content: '知', pinyin: 'zhī', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-zh2', section: 1, type: 'reading', content: '只', pinyin: 'zhǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-zh3', section: 1, type: 'reading', content: '主', pinyin: 'zhǔ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-zh4', section: 1, type: 'reading', content: '真', pinyin: 'zhēn', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-zh5', section: 1, type: 'reading', content: '张', pinyin: 'zhāng', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-zh6', section: 1, type: 'reading', content: '住', pinyin: 'zhù', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-zh7', section: 1, type: 'reading', content: '纸', pinyin: 'zhǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-zh8', section: 1, type: 'reading', content: '珠', pinyin: 'zhū', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-zh9', section: 1, type: 'reading', content: '逐', pinyin: 'zhú', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-zh10', section: 1, type: 'reading', content: '仲', pinyin: 'zhòng', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-zh11', section: 1, type: 'reading', content: '炸', pinyin: 'zhà', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-zh12', section: 1, type: 'reading', content: '症', pinyin: 'zhèng', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-zh13', section: 1, type: 'reading', content: '旨', pinyin: 'zhǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-zh14', section: 1, type: 'reading', content: '终', pinyin: 'zhōng', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  // ch (for comparison)
  { id: 's1-ch1', section: 1, type: 'reading', content: '尺', pinyin: 'chǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-ch2', section: 1, type: 'reading', content: '车', pinyin: 'chē', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-ch3', section: 1, type: 'reading', content: '吃', pinyin: 'chī', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-ch4', section: 1, type: 'reading', content: '出', pinyin: 'chū', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-ch5', section: 1, type: 'reading', content: '茶', pinyin: 'chá', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-ch6', section: 1, type: 'reading', content: '成', pinyin: 'chéng', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-ch7', section: 1, type: 'reading', content: '川', pinyin: 'chuān', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-ch8', section: 1, type: 'reading', content: '唱', pinyin: 'chàng', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-ch9', section: 1, type: 'reading', content: '潮', pinyin: 'cháo', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-ch10', section: 1, type: 'reading', content: '充', pinyin: 'chōng', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-ch11', section: 1, type: 'reading', content: '初', pinyin: 'chū', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-ch12', section: 1, type: 'reading', content: '彻', pinyin: 'chè', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-ch13', section: 1, type: 'reading', content: '除', pinyin: 'chú', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-ch14', section: 1, type: 'reading', content: '抽', pinyin: 'chōu', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-ch15', section: 1, type: 'reading', content: '程', pinyin: 'chéng', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  // sh (for comparison)
  { id: 's1-sh1', section: 1, type: 'reading', content: '十', pinyin: 'shí', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-sh2', section: 1, type: 'reading', content: '是', pinyin: 'shì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-sh3', section: 1, type: 'reading', content: '世', pinyin: 'shì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-sh4', section: 1, type: 'reading', content: '师', pinyin: 'shī', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-sh5', section: 1, type: 'reading', content: '书', pinyin: 'shū', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-sh6', section: 1, type: 'reading', content: '山', pinyin: 'shān', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-sh7', section: 1, type: 'reading', content: '上', pinyin: 'shàng', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-sh8', section: 1, type: 'reading', content: '少', pinyin: 'shǎo', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-sh9', section: 1, type: 'reading', content: '时', pinyin: 'shí', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-sh10', section: 1, type: 'reading', content: '使', pinyin: 'shǐ', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-sh11', section: 1, type: 'reading', content: '社', pinyin: 'shè', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-sh12', section: 1, type: 'reading', content: '手', pinyin: 'shǒu', tags: ['zcs_vs_zhchsh', 'tone_3'] },
  { id: 's1-sh13', section: 1, type: 'reading', content: '势', pinyin: 'shì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-sh14', section: 1, type: 'reading', content: '伸', pinyin: 'shēn', tags: ['zcs_vs_zhchsh', 'tone_1'] },
  { id: 's1-sh15', section: 1, type: 'reading', content: '石', pinyin: 'shí', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-sh16', section: 1, type: 'reading', content: '胜', pinyin: 'shèng', tags: ['zcs_vs_zhchsh', 'tone_4'] },
  { id: 's1-sh17', section: 1, type: 'reading', content: '舌', pinyin: 'shé', tags: ['zcs_vs_zhchsh', 'tone_2'] },
  { id: 's1-sh18', section: 1, type: 'reading', content: '室', pinyin: 'shì', tags: ['zcs_vs_zhchsh', 'tone_4'] },
];

// Section 2: Polysyllabic words
export const section2Questions: Question[] = [
  { id: 's2-1', section: 2, type: 'reading', content: '中国', pinyin: 'zhōngguó', tags: ['retroflex', 'tone_1', 'tone_2'] },
  { id: 's2-2', section: 2, type: 'reading', content: '人民', pinyin: 'rénmín', tags: ['tone_2', 'tone_2'] },
  { id: 's2-3', section: 2, type: 'reading', content: '学习', pinyin: 'xuéxí', tags: ['tone_2', 'tone_2'] },
  { id: 's2-4', section: 2, type: 'reading', content: '汉语', pinyin: 'hànyǔ', tags: ['tone_4', 'tone_3'] },
  { id: 's2-5', section: 2, type: 'reading', content: '朋友', pinyin: 'péngyou', tags: ['tone_2', 'neutral_tone'] },
  { id: 's2-6', section: 2, type: 'reading', content: '老师', pinyin: 'lǎoshī', tags: ['tone_3', 'tone_1'] },
  { id: 's2-7', section: 2, type: 'reading', content: '学生', pinyin: 'xuéshēng', tags: ['tone_2', 'tone_1'] },
  { id: 's2-8', section: 2, type: 'reading', content: '工作', pinyin: 'gōngzuò', tags: ['tone_1', 'tone_4'] },
  { id: 's2-9', section: 2, type: 'reading', content: '学校', pinyin: 'xuéxiào', tags: ['tone_2', 'tone_4'] },
  { id: 's2-10', section: 2, type: 'reading', content: '图书馆', pinyin: 'túshūguǎn', tags: ['tone_2', 'tone_1', 'tone_3'] },
  // an vs ang
  { id: 's2-11', section: 2, type: 'reading', content: '安', pinyin: 'ān', tags: ['an_vs_ang', 'tone_1'] },
  { id: 's2-12', section: 2, type: 'reading', content: '昂', pinyin: 'áng', tags: ['an_vs_ang', 'tone_2'] },
  { id: 's2-13', section: 2, type: 'reading', content: '看', pinyin: 'kàn', tags: ['an_vs_ang', 'tone_4'] },
  { id: 's2-14', section: 2, type: 'reading', content: '抗', pinyin: 'kàng', tags: ['an_vs_ang', 'tone_4'] },
  // en vs eng
  { id: 's2-15', section: 2, type: 'reading', content: '门', pinyin: 'mén', tags: ['en_vs_eng', 'tone_2'] },
  { id: 's2-16', section: 2, type: 'reading', content: '蒙', pinyin: 'méng', tags: ['en_vs_eng', 'tone_2'] },
  // in vs ing
  { id: 's2-17', section: 2, type: 'reading', content: '民', pinyin: 'mín', tags: ['in_vs_ing', 'tone_2'] },
  { id: 's2-18', section: 2, type: 'reading', content: '名', pinyin: 'míng', tags: ['in_vs_ing', 'tone_2'] },
  // Third tone sandhi
  { id: 's2-19', section: 2, type: 'reading', content: '你好', pinyin: 'nǐ hǎo', tags: ['third_tone', 'tone_3', 'tone_3'] },
  { id: 's2-20', section: 2, type: 'reading', content: '可以', pinyin: 'kě yǐ', tags: ['third_tone', 'tone_3'] },
];

// Section 3: Vocabulary and Grammar
export const section3Questions: Question[] = [
  { id: 's3-1', section: 3, type: 'choice', content: '请问，去图书馆怎么走？', options: ['左转', '右手', '汽车', '书本'], correctAnswer: '左转', tags: ['vocabulary'] },
  { id: 's3-2', section: 3, type: 'choice', content: '我___一本书。', options: ['本', '个', '条', '张'], correctAnswer: '本', tags: ['classifier'] },
  { id: 's3-3', section: 3, type: 'choice', content: '他已经___了。', options: ['吃', '吃了', '吃饭', '好吃'], correctAnswer: '吃了', tags: ['le_structure'] },
  { id: 's3-4', section: 3, type: 'choice', content: '我把窗户___。', options: ['开', '打开', '关上', '看'], correctAnswer: '打开', tags: ['passive_ba'] },
  { id: 's3-5', section: 3, type: 'choice', content: '这件事___很重要。', options: ['很', '非常', '特别', '最'], correctAnswer: '非常', tags: ['vocabulary'] },
  { id: 's3-6', section: 3, type: 'choice', content: '你___时候来的？', options: ['什么', '怎么', '哪', '这里'], correctAnswer: '什么', tags: ['vocabulary'] },
  { id: 's3-7', section: 3, type: 'choice', content: '我昨天___电影。', options: ['看', '看了', '看书', '好看'], correctAnswer: '看了', tags: ['le_structure'] },
  { id: 's3-8', section: 3, type: 'choice', content: '桌子上有一___书。', options: ['本', '只', '条', '件'], correctAnswer: '本', tags: ['classifier'] },
];

// Section 4: Reading passages
export const section4Questions: Question[] = [
  { id: 's4-1', section: 4, type: 'reading', content: '春天的花开得很美丽。', pinyin: 'chūntiān de huā kāi de hěn měilì', tags: ['neutral_tone'] },
  { id: 's4-2', section: 4, type: 'reading', content: '今天天气很好，我的心情也不错。', pinyin: 'jīntiān tiānqì hěn hǎo, wǒ de xīnqíng yě bùcuò', tags: ['third_tone', 'neutral_tone'] },
  { id: 's4-3', section: 4, type: 'reading', content: '学习和休息要合理安排。', pinyin: 'xuéxí hé xiūxi yào hé lǐ ānpái', tags: ['tone_2'] },
];

// Get all questions
export function getAllQuestions(): Question[] {
  return [...section1Questions, ...section2Questions, ...section3Questions, ...section4Questions];
}

// Get questions by section
export function getQuestionsBySection(section: 1 | 2 | 3 | 4 | 5): Question[] {
  switch (section) {
    case 1: return section1Questions;
    case 2: return section2Questions;
    case 3: return section3Questions;
    case 4: return section4Questions;
    default: return [];
  }
}

// Filter questions by tags
export function getQuestionsByTags(tags: string[]): Question[] {
  const allQuestions = getAllQuestions();
  if (tags.length === 0) return allQuestions;

  return allQuestions.filter(q =>
    q.tags && q.tags.some(tag => tags.includes(tag))
  );
}

// Fisher-Yates shuffle
function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// Get random questions
export function getRandomQuestions(count: number, tags?: string[]): Question[] {
  let questions = tags && tags.length > 0 ? getQuestionsByTags(tags) : getAllQuestions();

  // Shuffle using Fisher-Yates
  questions = shuffleArray(questions);

  return questions.slice(0, Math.min(count, questions.length));
}
