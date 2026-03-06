/**
 * PSC Question Generator
 * Generates questions with proper 70/30 distribution from word lists
 */

import {
  wordList1,
  wordList2,
  dialectTable,
  classifierTable,
  grammarTable,
  readingPassages,
  speakingTopics,
  SECTION_CONFIG
} from '../data/psc';

import type { PSCWord, DialectItem, ClassifierItem, GrammarItem, ReadingPassage, SpeakingTopic } from '../data/psc';

export interface Question {
  id: string;
  section: 1 | 2 | 3 | 4 | 5;
  type: 'reading' | 'choice' | 'speaking';
  content: string;
  pinyin?: string;
  options?: string[];
  correctAnswer?: string;
  category?: string;
  difficulty?: string;
}

// Seedable random number generator for reproducible tests
class SeededRandom {
  private seed: number;

  constructor(seed: number = Date.now()) {
    this.seed = seed;
  }

  next(): number {
    this.seed = (this.seed * 1103515245 + 12345) & 0x7fffffff;
    return this.seed / 0x7fffffff;
  }

  nextInt(min: number, max: number): number {
    return Math.floor(this.next() * (max - min + 1)) + min;
  }

  shuffle<T>(array: T[]): T[] {
    const result = [...array];
    for (let i = result.length - 1; i > 0; i--) {
      const j = Math.floor(this.next() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }
}

/**
 * Generate Section 1 questions (100 single characters)
 * 70% from List 1, 30% from List 2
 */
export function generateSection1Questions(count: number = 100, seed?: number): Question[] {
  const rng = new SeededRandom(seed);
  const list1Chars = wordList1.filter(w => w.syllables === 1);
  const list2Chars = wordList2.filter(w => w.syllables === 1);

  const list1Count = Math.floor(count * 0.7);
  const list2Count = count - list1Count;

  const selectedList1 = rng.shuffle(list1Chars).slice(0, list1Count);
  const selectedList2 = rng.shuffle(list2Chars).slice(0, list2Count);

  const allSelected = [...selectedList1, ...selectedList2];
  const shuffled = rng.shuffle(allSelected);

  return shuffled.map((word, index) => ({
    id: `s1-${index + 1}`,
    section: 1 as const,
    type: 'reading' as const,
    content: word.content,
    pinyin: word.pinyin,
    category: word.category || 'general',
    difficulty: word.category ? 'hard' : 'easy'
  }));
}

/**
 * Generate Section 2 questions (100 syllables worth of words)
 * 70% from List 1, 30% from List 2
 * Need to count syllables, not words
 */
export function generateSection2Questions(targetSyllables: number = 100, seed?: number): Question[] {
  const rng = new SeededRandom(seed);

  // Filter to only multi-syllable words
  const list1Words = wordList1.filter(w => w.syllables >= 2);
  const list2Words = wordList2.filter(w => w.syllables >= 2);

  // Calculate ratio
  const list1Ratio = 0.7;
  const targetList1Syllables = Math.floor(targetSyllables * list1Ratio);

  const questions: Question[] = [];
  let currentSyllables = 0;
  let list1Used = 0;
  let list2Used = 0;

  // Shuffle lists
  const shuffledList1 = rng.shuffle(list1Words);
  const shuffledList2 = rng.shuffle(list2Words);

  let list1Index = 0;
  let list2Index = 0;

  while (currentSyllables < targetSyllables) {
    let selected: PSCWord | null = null;

    // Determine if we should use List1 or List2 based on ratio
    const currentList1Ratio = list1Used / (currentSyllables || 1);

    if (currentList1Ratio < list1Ratio && list1Index < shuffledList1.length) {
      selected = shuffledList1[list1Index++];
      list1Used += selected.syllables;
    } else if (list2Index < shuffledList2.length) {
      selected = shuffledList2[list2Index++];
      list2Used += selected.syllables;
    } else if (list1Index < shuffledList1.length) {
      selected = shuffledList1[list1Index++];
      list1Used += selected.syllables;
    } else {
      break; // No more words
    }

    if (selected && currentSyllables + selected.syllables <= targetSyllables) {
      questions.push({
        id: `s2-${questions.length + 1}`,
        section: 2 as const,
        type: 'reading' as const,
        content: selected.content,
        pinyin: selected.pinyin,
        category: selected.category || 'general',
        difficulty: selected.category ? 'hard' : 'easy'
      });
      currentSyllables += selected.syllables;
    }
  }

  // Return shuffled for display (not in syllable order)
  return rng.shuffle(questions);
}

/**
 * Generate Section 3 questions (10 word judgment + 10 classifier + 5 grammar)
 */
export function generateSection3Questions(seed?: number): Question[] {
  const rng = new SeededRandom(seed);
  const questions: Question[] = [];

  // Part 1: Word judgment (10 questions) - from dialect table
  const shuffledDialects = rng.shuffle(dialectTable).slice(0, 10);
  shuffledDialects.forEach((item, index) => {
    // Create multiple choice from dialects
    const dialectWords = Object.values(item.dialects);
    const options = [
      item.standard,
      ...rng.shuffle(dialectWords).slice(0, 3)
    ].slice(0, 4);

    // Shuffle so correct answer isn't always first
    const shuffledOptions = rng.shuffle(options);
    const correctIndex = shuffledOptions.indexOf(item.standard);

    questions.push({
      id: `s3-w${index + 1}`,
      section: 3 as const,
      type: 'choice' as const,
      content: `下列詞語中，哪個是普通話規範說法？`,
      options: shuffledOptions.map((opt, i) => String.fromCharCode(65 + i) + '. ' + opt),
      correctAnswer: String.fromCharCode(65 + correctIndex),
      category: 'word_judgment',
      difficulty: item.difficulty
    });
  });

  // Part 2: Classifier (10 questions)
  const shuffledClassifiers = rng.shuffle(classifierTable).slice(0, 10);
  shuffledClassifiers.forEach((item, index) => {
    // Create wrong options from other classifiers for same noun type
    const wrongOptions = classifierTable
      .filter(c => c.id !== item.id)
      .slice(0, 3)
      .map(c => c.classifier);

    const options = [
      item.classifier,
      ...rng.shuffle(wrongOptions)
    ].slice(0, 4);

    const shuffledOptions = rng.shuffle(options);
    const correctIndex = shuffledOptions.indexOf(item.classifier);

    questions.push({
      id: `s3-c${index + 1}`,
      section: 3 as const,
      type: 'choice' as const,
      content: `一${item.noun}（${item.nounPinyin}）`,
      options: shuffledOptions.map((opt, i) => String.fromCharCode(65 + i) + '. ' + opt + ` (${getPinyinForClassifier(opt)})`),
      correctAnswer: String.fromCharCode(65 + correctIndex),
      category: 'classifier',
      difficulty: item.difficulty
    });
  });

  // Part 3: Grammar (5 questions)
  const shuffledGrammar = rng.shuffle(grammarTable).slice(0, 5);
  shuffledGrammar.forEach((item, index) => {
    questions.push({
      id: `s3-g${index + 1}`,
      section: 3 as const,
      type: 'choice' as const,
      content: item.question,
      options: item.options,
      correctAnswer: item.correctAnswer,
      category: 'grammar',
      difficulty: item.difficulty
    });
  });

  return rng.shuffle(questions);
}

// Helper to get pinyin for classifier
function getPinyinForClassifier(classifier: string): string {
  const found = classifierTable.find(c => c.classifier === classifier);
  return found ? found.classifierPinyin : '';
}

/**
 * Generate Section 4 questions (reading passage)
 */
export function generateSection4Questions(count: number = 1, seed?: number): Question[] {
  const rng = new SeededRandom(seed);
  const shuffled = rng.shuffle(readingPassages).slice(0, count);

  return shuffled.map((passage, index) => ({
    id: `s4-${index + 1}`,
    section: 4 as const,
    type: 'reading' as const,
    content: passage.content,
    pinyin: passage.pinyin,
    category: passage.title,
    difficulty: passage.difficulty
  }));
}

/**
 * Generate Section 5 questions (speaking topics)
 * Returns 2 topics for user to choose from
 */
export function generateSection5Questions(seed?: number): Question[] {
  const rng = new SeededRandom(seed);
  const shuffled = rng.shuffle(speakingTopics).slice(0, 2);

  return shuffled.map((topic, index) => ({
    id: `s5-${index + 1}`,
    section: 5 as const,
    type: 'speaking' as const,
    content: topic.topic,
    category: topic.keywords?.join(', '),
    difficulty: 'medium'
  }));
}

/**
 * Generate a full test (all 5 sections)
 */
export function generateFullTest(seed?: number): Record<1 | 2 | 3 | 4 | 5, Question[]> {
  return {
    1: generateSection1Questions(100, seed),
    2: generateSection2Questions(100, seed),
    3: generateSection3Questions(seed),
    4: generateSection4Questions(1, seed),
    5: generateSection5Questions(seed)
  };
}

/**
 * Generate a partial test (specific section)
 */
export function generatePartialTest(
  section: 1 | 2 | 3 | 4 | 5,
  seed?: number
): Question[] {
  switch (section) {
    case 1:
      return generateSection1Questions(100, seed);
    case 2:
      return generateSection2Questions(100, seed);
    case 3:
      return generateSection3Questions(seed);
    case 4:
      return generateSection4Questions(1, seed);
    case 5:
      return generateSection5Questions(seed);
    default:
      return [];
  }
}

export default {
  generateSection1Questions,
  generateSection2Questions,
  generateSection3Questions,
  generateSection4Questions,
  generateSection5Questions,
  generateFullTest,
  generatePartialTest
};
