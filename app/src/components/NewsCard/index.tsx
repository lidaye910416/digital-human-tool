import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from '@tarojs/components';
import { NewsItem } from '../../../../shared/models';
import { CATEGORY_EMOJIS, CATEGORY_NAMES } from '../../../../shared/constants';

interface NewsCardProps {
  news: NewsItem;
  onRead?: () => void;
  onSpeak?: () => void;
  onDigitalHuman?: () => void;
  onFavorite?: () => void;
  isPlaying?: boolean;
}

const NewsCard: React.FC<NewsCardProps> = ({
  news,
  onRead,
  onSpeak,
  onDigitalHuman,
  onFavorite,
  isPlaying = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getGradeStyle = (grade: string) => {
    switch (grade) {
      case 'A+':
      case 'A':
        return styles.gradeA;
      case 'B':
        return styles.gradeB;
      case 'C':
        return styles.gradeC;
      default:
        return styles.gradeD;
    }
  };

  const getGradeText = (grade: string) => {
    switch (grade) {
      case 'A+':
        return '优秀';
      case 'A':
        return '良好';
      case 'B':
        return '一般';
      case 'C':
        return '较差';
      default:
        return '低质';
    }
  };

  const emoji = CATEGORY_EMOJIS[news.category] || '📰';
  const categoryName = CATEGORY_NAMES[news.category] || news.category;
  const title = news.title_zh || news.title_en || '';
  const summary = news.summary_zh || news.summary_en || '';
  const source = news.source_zh || news.source_en || '';
  const grade = news.quality?.grade || 'D';
  const score = news.quality?.total_100 || 0;

  return (
    <View style={[styles.card, isPlaying && styles.cardPlaying]}>
      {/* Card Header */}
      <View style={styles.header}>
        <View style={styles.emoji}>{emoji}</View>
        <View style={styles.meta}>
          <View style={styles.tags}>
            <View style={[styles.tag, styles[`tag_${news.lang}`]]}>
              <Text style={styles.tagText}>{news.lang === 'zh' ? '中文' : 'EN'}</Text>
            </View>
            <View style={styles.tag}>
              <Text style={styles.tagText}>{categoryName}</Text>
            </View>
          </View>
          <Text style={styles.source}>{source}</Text>
        </View>
        <View style={[styles.grade, getGradeStyle(grade)]}>
          <Text style={styles.gradeText}>{grade}</Text>
          <Text style={styles.gradeScore}>{score}分</Text>
        </View>
      </View>

      {/* Card Body */}
      <View style={styles.body}>
        <Text 
          style={styles.title} 
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {title}
        </Text>
        <Text style={styles.summary} numberOfLines={isExpanded ? undefined : 2}>
          {summary}
        </Text>
      </View>

      {/* Card Footer - Actions */}
      <View style={styles.footer}>
        <Text style={styles.date}>{news.published_at}</Text>
        <View style={styles.actions}>
          {/* Read button */}
          <TouchableOpacity style={styles.actionBtn} onClick={onRead}>
            <Text style={styles.actionIcon}>📖</Text>
            <Text style={styles.actionText}>阅读</Text>
          </TouchableOpacity>

          {/* Speak button */}
          <TouchableOpacity 
            style={[styles.actionBtn, isPlaying && styles.actionBtnActive]} 
            onClick={onSpeak}
          >
            <Text style={styles.actionIcon}>🔊</Text>
            <Text style={[styles.actionText, isPlaying && styles.actionTextActive]}>
              {isPlaying ? '暂停' : '朗读'}
            </Text>
          </TouchableOpacity>

          {/* Digital Human button */}
          <TouchableOpacity style={styles.actionBtn} onClick={onDigitalHuman}>
            <Text style={styles.actionIcon}>🎬</Text>
            <Text style={styles.actionText}>播报</Text>
          </TouchableOpacity>

          {/* Favorite button */}
          <TouchableOpacity style={styles.actionBtn} onClick={onFavorite}>
            <Text style={styles.actionIcon}>{news.is_favorited ? '❤️' : '🤍'}</Text>
            <Text style={styles.actionText}>收藏</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#18181b',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  cardPlaying: {
    borderColor: '#6366f1',
    backgroundColor: 'rgba(99, 102, 241, 0.1)',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  emoji: {
    width: 44,
    height: 44,
    backgroundColor: '#27272a',
    borderRadius: 12,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 22,
    marginRight: 12,
  },
  meta: {
    flex: 1,
  },
  tags: {
    flexDirection: 'row',
    gap: 6,
    marginBottom: 4,
  },
  tag: {
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 6,
    backgroundColor: 'rgba(99, 102, 241, 0.15)',
  },
  tag_zh: {
    backgroundColor: 'rgba(249, 115, 22, 0.15)',
  },
  tag_en: {
    backgroundColor: 'rgba(59, 130, 246, 0.15)',
  },
  tagText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#a1a1aa',
    textTransform: 'uppercase',
  },
  source: {
    fontSize: 12,
    color: '#71717a',
  },
  grade: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
  gradeA: {
    backgroundColor: 'rgba(34, 197, 94, 0.15)',
  },
  gradeB: {
    backgroundColor: 'rgba(59, 130, 246, 0.15)',
  },
  gradeC: {
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
  },
  gradeD: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
  },
  gradeText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#22c55e',
  },
  gradeScore: {
    fontSize: 10,
    color: '#71717a',
  },
  body: {
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fafafa',
    lineHeight: 24,
    marginBottom: 8,
  },
  summary: {
    fontSize: 14,
    color: '#a1a1aa',
    lineHeight: 22,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.08)',
  },
  date: {
    fontSize: 11,
    color: '#71717a',
  },
  actions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingVertical: 6,
    paddingHorizontal: 10,
    backgroundColor: '#27272a',
    borderRadius: 8,
  },
  actionBtnActive: {
    backgroundColor: '#6366f1',
  },
  actionIcon: {
    fontSize: 14,
  },
  actionText: {
    fontSize: 12,
    color: '#a1a1aa',
  },
  actionTextActive: {
    color: '#ffffff',
  },
});

export default NewsCard;
