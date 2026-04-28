import { NewsItem, QualityScore } from '../models';

// Quality thresholds
const GRADE_THRESHOLDS = {
  'A+': 85,
  'A': 75,
  'B': 65,
  'C': 55,
  'D': 0
};

/**
 * Calculate quality grade from total score
 */
export function calculateGrade(totalScore: number): QualityScore['grade'] {
  if (totalScore >= GRADE_THRESHOLDS['A+']) return 'A+';
  if (totalScore >= GRADE_THRESHOLDS['A']) return 'A';
  if (totalScore >= GRADE_THRESHOLDS['B']) return 'B';
  if (totalScore >= GRADE_THRESHOLDS['C']) return 'C';
  return 'D';
}

/**
 * Filter news by minimum quality score
 * Default minimum is C grade (55 points)
 */
export function filterByQuality(news: NewsItem[], minGrade: number = 55): NewsItem[] {
  return news.filter(item => (item.quality?.total_100 || 0) >= minGrade);
}

/**
 * Check if news should be displayed (not too low quality)
 */
export function isDisplayable(news: NewsItem, showLowQuality: boolean = false): boolean {
  const score = news.quality?.total_100 || 0;
  if (!showLowQuality && score < 55) return false;
  return true;
}
