/**
 * PSC Scoring Engine
 * Implements exact PSC scoring formulas for all 5 sections
 */

import { SECTION_CONFIG, calculatePSCLevel } from '../../data/psc';

export interface PhoneticError {
  index: number;
  character: string;
  expected: string;
  actual: string;
  type: 'tone' | 'initial' | 'final' | 'whole';
  severity: 'error' | 'defect';
}

export interface PhoneticDefect {
  index: number;
  character: string;
  expected: string;
  actual: string;
  type: 'tone' | 'retroflex' | 'nasal' | 'r-coloring';
  description: string;
}

export interface TestResponse {
  questionId: string;
  audioUrl?: string;
  transcription?: string;
  errors: PhoneticError[];
  defects: PhoneticDefect[];
  duration?: number;
}

export interface SectionScore {
  section: 1 | 2 | 3 | 4 | 5;
  maxScore: number;
  rawScore: number;
  timeoutPenalty: number;
  finalScore: number;
  errorCount: number;
  defectCount: number;
  breakdown: ScoreBreakdown;
}

export interface ScoreBreakdown {
  [key: string]: {
    count?: number;
    deduction?: number;
    score?: number;
    max?: number;
    errors?: number;
  };
}

/** Letter grades for GPA (A=4.0, B+=3.0, C+=2.3, C=2.0, D=1.0) */
export type GPAGrade = 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D';

/** Grade to GPA: A=4.0, B+=3.0, C+=2.3, C=2.0, D=1.0 */
export function gradeToGPA(grade: string): number {
  const g: Record<string, number> = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.5,
    'B+': 3.0, 'B': 2.5, 'B-': 2.0,
    'C+': 2.3, 'C': 2.0,
    'D': 1.0
  };
  return g[grade] ?? 0;
}

/** Convert section score percentage (0–100) to letter grade for GPA */
export function scorePercentToGrade(percent: number): GPAGrade {
  if (percent >= 90) return 'A';
  if (percent >= 85) return 'B+';
  if (percent >= 80) return 'B';
  if (percent >= 70) return 'C+';
  if (percent >= 60) return 'C';
  return 'D';
}

export interface PSCRawResult {
  sections: {
    1?: SectionScore;
    2?: SectionScore;
    3?: SectionScore;
    4?: SectionScore;
    5?: SectionScore;
  };
  totalScore: number;
  level: string;
  grade: string;
  pass: boolean;
  timeUsed: number[];
  timeoutOccurred: boolean[];
  /** Letter grade per section (for GPA) */
  sectionGrades?: Partial<Record<1 | 2 | 3 | 4 | 5, string>>;
  /** GPA per section (A=4, B+=3, C=2, D=1) */
  sectionGPAs?: Partial<Record<1 | 2 | 3 | 4 | 5, number>>;
  /** Test GPA = average of section GPAs */
  testGPA?: number;
}

/**
 * Calculate Section 1 Score (Read Single Characters)
 * Max: 10 points
 * - Phonetic error: -0.1 per error
 * - Phonetic defect: -0.05 per defect
 * - Timeout <1min: -0.5
 * - Timeout >=1min: -1
 */
export function calculateSection1Score(
  response: TestResponse,
  duration: number,
  timeLimit: number = SECTION_CONFIG[1].timeLimit
): SectionScore {
  const config = SECTION_CONFIG[1];
  const errorCount = response.errors.length;
  const defectCount = response.defects.length;

  // Calculate timeout penalty
  let timeoutPenalty = 0;
  const timeOver = timeLimit - duration;
  if (timeOver > 60) {
    timeoutPenalty = config.timeoutPenalty.over1min;
  } else if (timeOver > 0) {
    timeoutPenalty = config.timeoutPenalty.under1min;
  }

  // Calculate raw score
  const errorDeduction = errorCount * 0.1;
  const defectDeduction = defectCount * 0.05;
  const rawScore = Math.max(0, config.maxScore - errorDeduction - defectDeduction);

  // Apply timeout penalty
  const finalScore = Math.max(0, rawScore - timeoutPenalty);

  return {
    section: 1,
    maxScore: config.maxScore,
    rawScore: Math.round(rawScore * 10) / 10,
    timeoutPenalty,
    finalScore: Math.round(finalScore * 10) / 10,
    errorCount,
    defectCount,
    breakdown: {
      phoneticErrors: { count: errorCount, deduction: errorDeduction },
      phoneticDefects: { count: defectCount, deduction: defectDeduction },
      timeout: { count: timeoutPenalty > 0 ? 1 : 0, deduction: timeoutPenalty }
    }
  };
}

/**
 * Calculate Section 2 Score (Read Polysyllabic Words)
 * Max: 20 points
 * - Phonetic error: -0.2 per error
 * - Phonetic defect: -0.1 per defect
 * - Timeout <1min: -0.5
 * - Timeout >=1min: -1
 */
export function calculateSection2Score(
  response: TestResponse,
  duration: number,
  timeLimit: number = SECTION_CONFIG[2].timeLimit
): SectionScore {
  const config = SECTION_CONFIG[2];
  const errorCount = response.errors.length;
  const defectCount = response.defects.length;

  // Calculate timeout penalty
  let timeoutPenalty = 0;
  const timeOver = timeLimit - duration;
  if (timeOver > 60) {
    timeoutPenalty = config.timeoutPenalty.over1min;
  } else if (timeOver > 0) {
    timeoutPenalty = config.timeoutPenalty.under1min;
  }

  // Calculate raw score
  const errorDeduction = errorCount * 0.2;
  const defectDeduction = defectCount * 0.1;
  const rawScore = Math.max(0, config.maxScore - errorDeduction - defectDeduction);

  // Apply timeout penalty
  const finalScore = Math.max(0, rawScore - timeoutPenalty);

  return {
    section: 2,
    maxScore: config.maxScore,
    rawScore: Math.round(rawScore * 10) / 10,
    timeoutPenalty,
    finalScore: Math.round(finalScore * 10) / 10,
    errorCount,
    defectCount,
    breakdown: {
      phoneticErrors: { count: errorCount, deduction: errorDeduction },
      phoneticDefects: { count: defectCount, deduction: defectDeduction },
      timeout: { count: timeoutPenalty > 0 ? 1 : 0, deduction: timeoutPenalty }
    }
  };
}

/**
 * Calculate Section 3 Score (Choice & Judgment)
 * Max: 10 points
 * - Word judgment error: -0.25 per group
 * - Classifier error: -0.5 per group
 * - Grammar error: -0.5 per group
 * - Phonetic error: -0.1 per error
 * - Timeout penalties
 */
export interface Section3Answers {
  wordJudgment: { questionId: string; userAnswer: string; correctAnswer: string }[];
  classifier: { questionId: string; userAnswer: string; correctAnswer: string }[];
  grammar: { questionId: string; userAnswer: string; correctAnswer: string }[];
}

export function calculateSection3Score(
  answers: Section3Answers,
  duration: number,
  timeLimit: number = SECTION_CONFIG[3].timeLimit
): SectionScore {
  const config = SECTION_CONFIG[3];
  const deductions = config.deductionRules;

  // Count errors in each category
  const wordJudgmentErrors = answers.wordJudgment.filter(
    a => a.userAnswer !== a.correctAnswer
  ).length;
  const classifierErrors = answers.classifier.filter(
    a => a.userAnswer !== a.correctAnswer
  ).length;
  const grammarErrors = answers.grammar.filter(
    a => a.userAnswer !== a.correctAnswer
  ).length;

  // Calculate deductions
  const wordJudgmentDeduction = wordJudgmentErrors * deductions.wordJudgment;
  const classifierDeduction = classifierErrors * deductions.classifier;
  const grammarDeduction = grammarErrors * deductions.grammar;

  // Calculate timeout penalty
  let timeoutPenalty = 0;
  const timeOver = timeLimit - duration;
  if (timeOver > 60) {
    timeoutPenalty = config.timeoutPenalty.over1min;
  } else if (timeOver > 0) {
    timeoutPenalty = config.timeoutPenalty.under1min;
  }

  // Calculate final score
  const rawScore = Math.max(0,
    config.maxScore - wordJudgmentDeduction - classifierDeduction - grammarDeduction
  );
  const finalScore = Math.max(0, rawScore - timeoutPenalty);

  return {
    section: 3,
    maxScore: config.maxScore,
    rawScore: Math.round(rawScore * 10) / 10,
    timeoutPenalty,
    finalScore: Math.round(finalScore * 10) / 10,
    errorCount: wordJudgmentErrors + classifierErrors + grammarErrors,
    defectCount: 0,
    breakdown: {
      wordJudgment: { count: wordJudgmentErrors, deduction: wordJudgmentDeduction },
      classifier: { count: classifierErrors, deduction: classifierDeduction },
      grammar: { count: grammarErrors, deduction: grammarDeduction },
      timeout: { count: timeoutPenalty > 0 ? 1 : 0, deduction: timeoutPenalty }
    }
  };
}

/**
 * Calculate Section 4 Score (Reading Passage)
 * Max: 30 points
 * - Misread/omitted/added: -0.1 per character
 * - Tone defects: -0.5/1 per instance
 * - Intonation errors: -0.5/1/2
 * - Pause errors: -0.5/1/2
 * - Disfluency: -0.5/1/2
 * - Timeout: -1
 */
export function calculateSection4Score(
  response: TestResponse,
  duration: number,
  timeLimit: number = SECTION_CONFIG[4].timeLimit
): SectionScore {
  const config = SECTION_CONFIG[4];
  const errorCount = response.errors.filter(e => e.severity === 'error').length;
  const defectCount = response.defects.length;

  // Calculate timeout penalty
  let timeoutPenalty = 0;
  const timeOver = timeLimit - duration;
  if (timeOver > 0) {
    timeoutPenalty = config.timeoutPenalty;
  }

  // For now, use simplified calculation
  // In production, you'd need detailed per-character analysis from iFlytek
  const misreadDeduction = errorCount * config.deductionRules.misread;
  const toneDefectDeduction = defectCount * config.deductionRules.toneDefect;

  const rawScore = Math.max(0,
    config.maxScore - misreadDeduction - toneDefectDeduction
  );
  const finalScore = Math.max(0, rawScore - timeoutPenalty);

  return {
    section: 4,
    maxScore: config.maxScore,
    rawScore: Math.round(rawScore * 10) / 10,
    timeoutPenalty,
    finalScore: Math.round(finalScore * 10) / 10,
    errorCount,
    defectCount,
    breakdown: {
      misreads: { count: errorCount, deduction: misreadDeduction },
      toneDefects: { count: defectCount, deduction: toneDefectDeduction },
      timeout: { count: timeoutPenalty > 0 ? 1 : 0, deduction: timeoutPenalty }
    }
  };
}

/**
 * Calculate Section 5 Score (Topic Speaking)
 * Max: 30 points
 * - Pronunciation: 20 points (6 levels)
 * - Vocabulary/Grammar: 5 points (3 levels)
 * - Fluency: 5 points (3 levels)
 * - Time deductions for short responses
 */
export interface Section5Analysis {
  pronunciationScore: number;
  vocabularyScore: number;
  fluencyScore: number;
  pronunciationErrors: number;
  vocabularyIssues: number;
  fluencyIssues: number;
}

export function calculateSection5Score(
  analysis: Section5Analysis,
  duration: number,
  timeLimit: number = SECTION_CONFIG[5].timeLimit
): SectionScore {
  const config = SECTION_CONFIG[5];
  const subScores = config.subScores;

  // Calculate time deduction
  let timeDeduction = 0;
  if (duration < 30) {
    // Less than 30 seconds = automatic fail for this section
    timeDeduction = 30;
  } else if (duration < 60) {
    timeDeduction = config.timeDeduction.under1min[2]; // -3
  } else if (duration < timeLimit) {
    // Within limit, no penalty
    timeDeduction = 0;
  } else {
    // Over time limit
    const timeOver = duration - timeLimit;
    if (timeOver < 60) {
      timeDeduction = config.timeDeduction.over1min[2]; // -6
    } else {
      timeDeduction = config.timeDeduction.over1min[2];
    }
  }

  // Calculate final scores for each component
  const pronunciationFinal = Math.max(0, subScores.pronunciation - analysis.pronunciationScore);
  const vocabularyFinal = Math.max(0, subScores.vocabulary - analysis.vocabularyScore);
  const fluencyFinal = Math.max(0, subScores.fluency - analysis.fluencyScore);

  const rawScore = pronunciationFinal + vocabularyFinal + fluencyFinal;
  const finalScore = Math.max(0, rawScore - timeDeduction);

  return {
    section: 5,
    maxScore: config.maxScore,
    rawScore: Math.round(rawScore * 10) / 10,
    timeoutPenalty: timeDeduction,
    finalScore: Math.round(finalScore * 10) / 10,
    errorCount: analysis.pronunciationErrors,
    defectCount: analysis.vocabularyIssues + analysis.fluencyIssues,
    breakdown: {
      pronunciation: {
        score: subScores.pronunciation - pronunciationFinal,
        max: subScores.pronunciation,
        errors: analysis.pronunciationErrors
      },
      vocabulary: {
        score: subScores.vocabulary - vocabularyFinal,
        max: subScores.vocabulary,
        errors: analysis.vocabularyIssues
      },
      fluency: {
        score: subScores.fluency - fluencyFinal,
        max: subScores.fluency,
        errors: analysis.fluencyIssues
      },
      timeout: { count: timeDeduction > 0 ? 1 : 0, deduction: timeDeduction }
    }
  };
}

/**
 * Calculate full PSC test score
 */
export function calculateFullPSCScore(
  responses: {
    section1?: TestResponse;
    section2?: TestResponse;
    section3?: Section3Answers;
    section4?: TestResponse;
    section5?: Section5Analysis;
  },
  durations: {
    section1?: number;
    section2?: number;
    section3?: number;
    section4?: number;
    section5?: number;
  }
): PSCRawResult {
  const sections: PSCRawResult['sections'] = {};
  const timeUsed: number[] = [];
  const timeoutOccurred: boolean[] = [];

  // Section 1
  if (responses.section1 && durations.section1 !== undefined) {
    sections[1] = calculateSection1Score(responses.section1, durations.section1);
    timeUsed.push(durations.section1);
    timeoutOccurred.push(durations.section1 > SECTION_CONFIG[1].timeLimit);
  }

  // Section 2
  if (responses.section2 && durations.section2 !== undefined) {
    sections[2] = calculateSection2Score(responses.section2, durations.section2);
    timeUsed.push(durations.section2);
    timeoutOccurred.push(durations.section2 > SECTION_CONFIG[2].timeLimit);
  }

  // Section 3
  if (responses.section3 && durations.section3 !== undefined) {
    sections[3] = calculateSection3Score(responses.section3, durations.section3);
    timeUsed.push(durations.section3);
    timeoutOccurred.push(durations.section3 > SECTION_CONFIG[3].timeLimit);
  }

  // Section 4
  if (responses.section4 && durations.section4 !== undefined) {
    sections[4] = calculateSection4Score(responses.section4, durations.section4);
    timeUsed.push(durations.section4);
    timeoutOccurred.push(durations.section4 > SECTION_CONFIG[4].timeLimit);
  }

  // Section 5
  if (responses.section5 && durations.section5 !== undefined) {
    sections[5] = calculateSection5Score(responses.section5, durations.section5);
    timeUsed.push(durations.section5);
    timeoutOccurred.push(durations.section5 > SECTION_CONFIG[5].timeLimit);
  }

  // Calculate total
  let totalScore = 0;
  for (const section of Object.values(sections)) {
    if (section) {
      totalScore += section.finalScore;
    }
  }

  // Determine level
  const levelInfo = calculatePSCLevel(totalScore);

  // Per-section GPA and test GPA (average of section GPAs)
  const sectionGrades: Partial<Record<1 | 2 | 3 | 4 | 5, string>> = {};
  const sectionGPAs: Partial<Record<1 | 2 | 3 | 4 | 5, number>> = {};
  const gpaValues: number[] = [];
  for (const [key, section] of Object.entries(sections)) {
    if (!section) continue;
    const sectionNum = parseInt(key, 10) as 1 | 2 | 3 | 4 | 5;
    const percent = section.maxScore > 0 ? (section.finalScore / section.maxScore) * 100 : 0;
    const grade = scorePercentToGrade(percent);
    const gpa = gradeToGPA(grade);
    sectionGrades[sectionNum] = grade;
    sectionGPAs[sectionNum] = gpa;
    gpaValues.push(gpa);
  }
  const testGPA = gpaValues.length > 0
    ? Math.round((gpaValues.reduce((a, b) => a + b, 0) / gpaValues.length) * 100) / 100
    : undefined;

  return {
    sections,
    totalScore: Math.round(totalScore * 10) / 10,
    level: levelInfo.level,
    grade: levelInfo.grade,
    pass: totalScore >= 60,
    timeUsed,
    timeoutOccurred,
    sectionGrades,
    sectionGPAs,
    testGPA
  };
}

export default {
  calculateSection1Score,
  calculateSection2Score,
  calculateSection3Score,
  calculateSection4Score,
  calculateSection5Score,
  calculateFullPSCScore,
  gradeToGPA,
  scorePercentToGrade
};
