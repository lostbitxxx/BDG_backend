import express, { Request, Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Load local PSC data
let pscData: {
  part1: any[];
  part2: any[];
  part3: any[];
  part4: any[];
  part5: any[];
} | null = null;

function loadPSCData() {
  if (pscData) return pscData;

  const docsPath = path.join(__dirname, '../../docs/psc-data');

  try {
    // Load Part 1 - Single characters
    const part1Path = path.join(docsPath, 'part1_single_characters/chars.json');
    const part1 = fs.existsSync(part1Path) ? JSON.parse(fs.readFileSync(part1Path, 'utf-8')) : [];

    // Load Part 2 - Multi-syllable words
    const part2Path = path.join(docsPath, 'part2_multi_syllable_words/words.json');
    const part2 = fs.existsSync(part2Path) ? JSON.parse(fs.readFileSync(part2Path, 'utf-8')) : [];

    // Load Part 3 - Choice questions
    const part3Path = path.join(docsPath, 'part3_choice_judgment/questions.json');
    const part3 = fs.existsSync(part3Path) ? JSON.parse(fs.readFileSync(part3Path, 'utf-8')) : [];

    // Load Part 4 - Reading passages
    const part4Path = path.join(docsPath, 'part4_reading_passages/passages.json');
    const part4 = fs.existsSync(part4Path) ? JSON.parse(fs.readFileSync(part4Path, 'utf-8')) : [];

    // Load Part 5 - Speaking topics
    const part5Path = path.join(docsPath, 'part5_speaking_topics/topics.json');
    const part5 = fs.existsSync(part5Path) ? JSON.parse(fs.readFileSync(part5Path, 'utf-8')) : [];

    pscData = { part1, part2, part3, part4, part5 };
    console.log('PSC Data loaded:', {
      part1: part1.length,
      part2: part2.length,
      part3: part3.length,
      part4: part4.length,
      part5: part5.length
    });

    return pscData;
  } catch (error) {
    console.error('Error loading PSC data:', error);
    return { part1: [], part2: [], part3: [], part4: [], part5: [] };
  }
}

// POST /api/questions/generate
router.post('/generate', authenticateToken, async (req: Request, res: Response) => {
  const { section, count = 10 } = req.body as {
    section: number;
    count?: number;
  };

  if (!section || section < 1 || section > 5) {
    return res.status(400).json({ success: false, error: 'Invalid section (1-5)' });
  }

  try {
    const data = loadPSCData();
    let questions: any[] = [];

    // Use local data based on section
    switch (section) {
      case 1: // Single characters
        questions = shuffleArray([...data.part1]).slice(0, count).map((q: any, idx: number) => ({
          id: `s1-${idx + 1}`,
          content: q.content,
          pinyin: q.pinyin || ''
        }));
        break;

      case 2: // Multi-syllable words
        questions = shuffleArray([...data.part2]).slice(0, count).map((q: any, idx: number) => ({
          id: `s2-${idx + 1}`,
          content: q.content,
          pinyin: q.pinyin || ''
        }));
        break;

      case 3: // Choice questions
        questions = shuffleArray([...data.part3]).slice(0, count).map((q: any, idx: number) => ({
          id: `s3-${idx + 1}`,
          type: q.type,
          content: q.question,
          options: q.options,
          correctAnswer: q.correctAnswer
        }));
        break;

      case 4: // Reading passages
        questions = shuffleArray([...data.part4]).slice(0, count).map((q: any, idx: number) => ({
          id: `s4-${idx + 1}`,
          content: q.content
        }));
        break;

      case 5: // Speaking topics
        questions = shuffleArray([...data.part5]).slice(0, count).map((q: any, idx: number) => ({
          id: `s5-${idx + 1}`,
          content: q.content
        }));
        break;
    }

    // If not enough data in local database, use fallback
    if (questions.length < count) {
      console.log(`Not enough local data for section ${section}, using fallback`);
      const fallback = generateFallbackQuestions(section, count);
      questions = [...questions, ...fallback].slice(0, count);
    }

    res.json({ success: true, section, count: questions.length, questions });

  } catch (error) {
    console.error('Question generation error:', error);
    const questions = generateFallbackQuestions(section, count);
    res.json({ success: true, section, count: questions.length, questions });
  }
});

// Shuffle array using Fisher-Yates algorithm
function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// Fallback questions when local data is insufficient
function generateFallbackQuestions(section: number, count: number): any[] {
  const chars = '一二三四五六七八九十百千万亿人口手足口耳目头心天地日月星水火山石土木金玉竹米谷茶';
  const words = ['春天', '夏天', '秋天', '冬天', '中国', '学习', '工作', '生活', '时间', '朋友', '家人', '老师', '学生', '学校', '公司', '医院', '银行', '车站', '机场', '酒店', '餐厅', '商场', '图书馆', '博物馆'];
  const topics = ['我的朋友', '我的家庭', '我的学习生活', '我的理想', '我最喜欢的季节', '我的一天', '我的童年', '我的兴趣爱好', '我喜爱的食物', '我喜欢的电影'];
  const passages = [
    '春天到了，万物复苏。阳光明媚，百花齐放。小草从土里钻出来，柳树抽出嫩绿的新芽。',
    '今天天气很好，蓝天白云，微风轻拂。树叶在风中轻轻摇摆，鸟儿在枝头歌唱。',
    '我的家乡是一个美丽的小镇，那里有很多古老的建筑和清澈的河流。',
    '学习普通话很重要，它可以帮助我们更好地与中国人交流。声调是普通话的特点。',
    '中国有五千年的悠久历史，文化底蕴深厚。春节是重要的传统节日。'
  ];

  if (section === 1) {
    const allChars = chars.split('');
    const selected: string[] = [];
    while (selected.length < count && selected.length < allChars.length) {
      const idx = Math.floor(Math.random() * allChars.length);
      if (!selected.includes(allChars[idx])) {
        selected.push(allChars[idx]);
      }
    }
    return selected.map((char, i) => ({
      id: `s1-fallback-${i + 1}`,
      content: char,
      pinyin: getPinyin(char)
    }));
  }

  if (section === 2) {
    const shuffled = [...words].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count).map((word, i) => ({
      id: `s2-fallback-${i + 1}`,
      content: word,
      pinyin: getPinyin(word)
    }));
  }

  if (section === 3) {
    return Array.from({ length: count }, (_, i) => ({
      id: `s3-fallback-${i + 1}`,
      type: 'word_judgment',
      content: '下列词语中，哪个是普通话规范说法？',
      options: ['A. 规范词A', 'B. 方言词B', 'C. 错误词C', 'D. 其他D'],
      correctAnswer: 'A'
    }));
  }

  if (section === 4) {
    const shuffled = [...passages].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count).map((passage, i) => ({
      id: `s4-fallback-${i + 1}`,
      content: passage
    }));
  }

  // Section 5
  const shuffled = [...topics].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count).map((topic, i) => ({
    id: `s5-fallback-${i + 1}`,
    content: topic
  }));
}

// Simple pinyin lookup
function getPinyin(char: string): string {
  const pinyinMap: Record<string, string> = {
    '一': 'yī', '二': 'èr', '三': 'sān', '四': 'sì', '五': 'wǔ',
    '六': 'liù', '七': 'qī', '八': 'bā', '九': 'jiǔ', '十': 'shí',
    '百': 'bǎi', '千': 'qiān', '万': 'wàn', '亿': 'yì',
    '春': 'chūn', '夏': 'xià', '秋': 'qiū', '冬': 'dōng',
    '天': 'tiān', '地': 'dì', '日': 'rì', '月': 'yuè', '星': 'xīng',
    '水': 'shuǐ', '火': 'huǒ', '山': 'shān', '石': 'shí',
    '木': 'mù', '土': 'tǔ', '金': 'jīn', '玉': 'yù', '竹': 'zhú',
    '米': 'mǐ', '谷': 'gǔ', '茶': 'chá',
    '人': 'rén', '口': 'kǒu', '手': 'shǒu', '足': 'zú',
    '耳': 'ěr', '目': 'mù', '头': 'tóu', '心': 'xīn',
    '中': 'zhōng', '国': 'guó', '学': 'xué', '习': 'xí',
    '工': 'gōng', '作': 'zuò', '生': 'shēng', '活': 'huó',
    '时': 'shí', '间': 'jiān', '朋': 'péng', '友': 'yǒu',
    '家': 'jiā', '庭': 'tíng', '老': 'lǎo', '师': 'shī',
    '校': 'xiào', '公': 'gōng', '司': 'sī', '医': 'yī',
    '银': 'yín', '行': 'háng', '车': 'chē', '站': 'zhàn',
    '机': 'jī', '场': 'chǎng', '店': 'diàn',
    '餐': 'cān', '厅': 'tīng', '商': 'shāng',
    '图': 'tú', '书': 'shū', '馆': 'guǎn', '博': 'bó',
    '物': 'wù'
  };

  let result = '';
  for (const c of char) {
    result += (pinyinMap[c] || c) + ' ';
  }
  return result.trim() || char;
}

export default router;
