// Category definitions
export const CATEGORIES = [
  { id: 'all', name: '推荐', emoji: '✨' },
  { id: 'ai', name: 'AI', emoji: '🤖' },
  { id: 'tools', name: '工具', emoji: '🔧' },
  { id: 'news', name: '动态', emoji: '📰' },
  { id: 'product', name: '产品', emoji: '💡' }
] as const;

export const CATEGORY_EMOJIS: Record<string, string> = {
  ai: '🤖',
  tools: '🔧',
  news: '📰',
  product: '💡'
};

export const CATEGORY_NAMES: Record<string, string> = {
  ai: 'AI',
  tools: '工具',
  news: '动态',
  product: '产品'
};

// Animation durations (ms)
export const ANIMATION = {
  FAST: 150,
  NORMAL: 250,
  SLOW: 400,
  SLOWER: 600
} as const;

// Easing functions
export const EASING = {
  OUT: 'cubic-bezier(0.16, 1, 0.3, 1)',
  IN_OUT: 'cubic-bezier(0.65, 0, 0.35, 1)',
  SPRING: 'cubic-bezier(0.34, 1.56, 0.64, 1)'
} as const;
