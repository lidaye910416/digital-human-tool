// News item interface - shared between all platforms
export interface QualityScore {
  total_100: number;
  weighted_total: number;
  grade: 'A+' | 'A' | 'B' | 'C' | 'D';
  scores: {
    completeness: number;
    language: number;
    title: number;
    source_credibility: number;
    info_density: number;
    actionability: number;
    impact: number;
    originality: number;
  };
  issues: string[];
}

export interface NewsItem {
  id: string;
  title_zh: string;
  title_en?: string;
  summary_zh: string;
  summary_en?: string;
  content_zh: string;
  content_en?: string;
  source_zh: string;
  source_en?: string;
  source_url: string;
  lang: 'zh' | 'en' | 'both';
  category: string;
  published_at: string;
  created_at: string;
  quality: QualityScore;
  is_read?: boolean;
  is_favorited?: boolean;
  audio_url?: string;
}

export interface NewsStats {
  total: number;
  zh: number;
  en: number;
  high: number; // A+, A, B grade
}

export type Category = 'all' | 'ai' | 'tools' | 'news' | 'product';
export type Language = 'zh' | 'en' | 'both';
