/**
 * PSC Data Index
 * Export all PSC data from a single entry point
 */

export { wordList1 } from './wordList1';
export type { PSCWord } from './wordList1';

export { wordList2 } from './wordList2';

export { dialectTable } from './dialectTable';
export type { DialectItem } from './dialectTable';

export { classifierTable } from './classifierTable';
export type { ClassifierItem } from './classifierTable';

export { grammarTable } from './grammarTable';
export type { GrammarItem } from './grammarTable';

export { readingPassages } from './readingPassages';
export type { ReadingPassage } from './readingPassages';

export { speakingTopics } from './speakingTopics';
export type { SpeakingTopic } from './speakingTopics';

// Section configurations
export const SECTION_CONFIG = {
  1: {
    name: '讀單音節字',
    nameEn: 'Read Single Characters',
    timeLimit: 210, // 3.5 minutes in seconds
    maxScore: 10,
    questionCount: 100,
    sourceRatio: { list1: 0.7, list2: 0.3 },
    timeoutPenalty: {
      under1min: 0.5,
      over1min: 1
    }
  },
  2: {
    name: '讀多音節詞語',
    nameEn: 'Read Polysyllabic Words',
    timeLimit: 150, // 2.5 minutes
    maxScore: 20,
    questionCount: 100, // 100 syllables
    sourceRatio: { list1: 0.7, list2: 0.3 },
    timeoutPenalty: {
      under1min: 0.5,
      over1min: 1
    }
  },
  3: {
    name: '選擇判斷',
    nameEn: 'Choice & Judgment',
    timeLimit: 180, // 3 minutes
    maxScore: 10,
    questionCount: 25, // 10 + 10 + 5
    subParts: {
      wordJudgment: 10,
      classifier: 10,
      grammar: 5
    },
    timeoutPenalty: {
      under1min: 0.5,
      over1min: 1
    },
    deductionRules: {
      wordJudgment: 0.25,
      classifier: 0.5,
      grammar: 0.5,
      phoneticError: 0.1
    }
  },
  4: {
    name: '朗讀短文',
    nameEn: 'Reading Passage',
    timeLimit: 300, // 5 minutes
    maxScore: 30,
    passageLength: 400, // characters
    timeoutPenalty: 1,
    deductionRules: {
      misread: 0.1,
      toneDefect: 0.5,
      intonation: [0.5, 1, 2],
      pause: [0.5, 1, 2],
      disfluency: [0.5, 1, 2]
    }
  },
  5: {
    name: '命題說話',
    nameEn: 'Topic Speaking',
    timeLimit: 180, // 3 minutes
    maxScore: 30,
    subScores: {
      pronunciation: 20, // 6 levels
      vocabulary: 5, // 3 levels
      fluency: 5 // 3 levels
    },
    timeDeduction: {
      under1min: [1, 2, 3],
      over1min: [4, 5, 6],
      under30sec: 30 // auto-fail
    }
  }
} as const;

// PSC Level definitions
export const PSC_LEVELS = [
  { min: 97, max: 100, level: '一級甲等', grade: 'A', description: ' Standard Mandarin' },
  { min: 92, max: 96.99, level: '一級乙等', grade: 'B', description: 'Near-native Mandarin' },
  { min: 87, max: 91.99, level: '二級甲等', grade: 'A', description: 'Good Mandarin for teaching' },
  { min: 80, max: 86.99, level: '二級乙等', grade: 'B', description: 'Acceptable Mandarin' },
  { min: 70, max: 79.99, level: '三級甲等', grade: 'A', description: 'Pass for civil service' },
  { min: 60, max: 69.99, level: '三級乙等', grade: 'B', description: 'Basic Mandarin' },
  { min: 0, max: 59.99, level: '不入級', grade: 'C', description: 'Below standard' },
] as const;

export function calculatePSCLevel(score: number) {
  for (const tier of PSC_LEVELS) {
    if (score >= tier.min && score <= tier.max) {
      return { ...tier, score };
    }
  }
  return PSC_LEVELS[PSC_LEVELS.length - 1];
}

export default {
  SECTION_CONFIG,
  PSC_LEVELS,
  calculatePSCLevel
};
