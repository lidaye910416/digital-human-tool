import { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import { getNewsList, getNewsStats, NewsItem, getDisplayTitle, getDisplaySource } from '../../api'
import './index.scss'

// 分类配置
const CATEGORIES = [
  { id: 'all', name: '推荐', emoji: '✨' },
  { id: 'ai', name: 'AI', emoji: '🤖' },
  { id: 'tools', name: '工具', emoji: '🔧' },
  { id: 'news', name: '动态', emoji: '📰' },
  { id: 'product', name: '产品', emoji: '💡' }
]

const CATEGORY_EMOJIS: Record<string, string> = {
  ai: '🤖',
  tools: '🔧',
  news: '📰',
  product: '💡'
}

export default function Index() {
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<{ lastUpdate: string; totalCount: number; stats: Record<string, number> } | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      // 加载统计信息
      const statsRes = await getNewsStats()
      if (statsRes.success) {
        setStats(statsRes.data)
      }

      // 加载最新资讯
      const newsRes = await getNewsList({ limit: 10 })
      if (newsRes.success && Array.isArray(newsRes.data)) {
        setNews(newsRes.data)
      }
    } catch (e) {
      console.error('Load data failed:', e)
    }
    setLoading(false)
  }

  const handleNewsClick = (item: NewsItem) => {
    // 跳转到资讯详情页
    Taro.navigateTo({
      url: `/pages/read/read?id=${item.id}`
    })
  }

  return (
    <View className="index-page">
      {/* 头部 */}
      <View className="header">
        <Text className="title">🎙️ Tech Echo</Text>
        <Text className="subtitle">科技资讯，有声播报</Text>
      </View>

      {/* 今日资讯 */}
      <View className="section">
        <View className="section-header">
          <Text className="section-title">📰 今日资讯</Text>
          <Text className="section-more">更多 →</Text>
        </View>

        {loading ? (
          <View className="loading">加载中...</View>
        ) : (
          <ScrollView scrollX className="news-scroll">
            {news.slice(0, 5).map(item => (
              <View
                key={item.id}
                className="news-card"
                onClick={() => handleNewsClick(item)}
              >
                <Text className="news-title">{getDisplayTitle(item)}</Text>
                <View className="news-meta">
                  <Text className="news-source">{getDisplaySource(item)}</Text>
                  <Text className="news-grade">
                    {item.quality?.grade || ''} {item.quality?.total_100 || 0}分
                  </Text>
                </View>
              </View>
            ))}
          </ScrollView>
        )}
      </View>

      {/* 快捷入口 */}
      <View className="section">
        <View className="section-header">
          <Text className="section-title">🚀 快捷功能</Text>
        </View>
        <View className="quick-actions">
          <View className="action-card" onClick={() => Taro.switchTab({ url: '/pages/news/news' })}>
            <Text className="action-icon">📋</Text>
            <Text className="action-text">浏览资讯</Text>
          </View>
          <View className="action-card">
            <Text className="action-icon">🔊</Text>
            <Text className="action-text">语音播报</Text>
          </View>
          <View className="action-card">
            <Text className="action-icon">🎬</Text>
            <Text className="action-text">数字人播报</Text>
            <Text className="action-badge">开发中</Text>
          </View>
        </View>
      </View>

      {/* 分类 */}
      <View className="section">
        <View className="section-header">
          <Text className="section-title">📂 分类浏览</Text>
        </View>
        <View className="category-grid">
          {CATEGORIES.filter(c => c.id !== 'all').map(cat => (
            <View key={cat.id} className="category-item">
              <Text className="category-emoji">{CATEGORY_EMOJIS[cat.id] || cat.emoji}</Text>
              <Text className="category-name">{cat.name}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* 统计信息 */}
      {stats && (
        <View className="section">
          <View className="section-header">
            <Text className="section-title">📊 数据统计</Text>
          </View>
          <View className="stats-grid">
            <View className="stat-item">
              <Text className="stat-value">{stats.totalCount}</Text>
              <Text className="stat-label">总资讯</Text>
            </View>
            <View className="stat-item">
              <Text className="stat-value">{stats.stats['A'] + stats.stats['A+'] || 0}</Text>
              <Text className="stat-label">优质(A/B)</Text>
            </View>
            <View className="stat-item">
              <Text className="stat-value">{stats.lastUpdate?.slice(0, 10) || '-'}</Text>
              <Text className="stat-label">更新时间</Text>
            </View>
          </View>
        </View>
      )}
    </View>
  )
}
