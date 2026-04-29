import { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import { getNewsList, getNewsStats, NewsItem, getDisplayTitle, getDisplaySource } from '../../api'
import './news.scss'

export default function News() {
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<{ categories: string[]; stats: Record<string, number> } | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  useEffect(() => {
    loadData()
  }, [selectedCategory])

  const loadData = async () => {
    setLoading(true)
    try {
      // 加载统计信息
      const statsRes = await getNewsStats()
      if (statsRes.success) {
        setStats(statsRes.data)
      }

      // 加载新闻列表
      const params: { category?: string; limit?: number } = { limit: 50 }
      if (selectedCategory !== 'all') {
        params.category = selectedCategory
      }
      const newsRes = await getNewsList(params)
      if (newsRes.success && Array.isArray(newsRes.data)) {
        setNews(newsRes.data)
      }
    } catch (e) {
      console.error('Load news failed:', e)
    }
    setLoading(false)
  }

  const handleNewsClick = (item: NewsItem) => {
    Taro.navigateTo({
      url: `/pages/read/read?id=${item.id}`
    })
  }

  const categories = stats?.categories || ['ai', 'product', 'news']

  return (
    <View className="news-page">
      {/* 分类选择 */}
      <ScrollView scrollX className="category-tabs">
        <View
          key="all"
          className={`category-tab ${selectedCategory === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('all')}
        >
          <Text className="category-text">全部</Text>
        </View>
        {categories.map(cat => (
          <View
            key={cat}
            className={`category-tab ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            <Text className="category-text">{cat.toUpperCase()}</Text>
          </View>
        ))}
      </ScrollView>

      {/* 统计信息 */}
      {stats && (
        <View className="stats-bar">
          <Text className="stats-text">
            共 {news.length} 条 | A/B级 {stats.stats['A'] + stats.stats['A+'] + stats.stats['B'] || 0} 条
          </Text>
        </View>
      )}

      {/* 资讯列表 */}
      <ScrollView scrollY className="news-list">
        {loading ? (
          <View className="loading">加载中...</View>
        ) : news.length === 0 ? (
          <View className="empty">
            <Text className="empty-icon">📭</Text>
            <Text className="empty-text">暂无资讯</Text>
            <Text className="empty-hint">请选择其他分类查看</Text>
          </View>
        ) : (
          news.map(item => (
            <View
              key={item.id}
              className={`news-item ${item.is_read ? 'read' : ''}`}
              onClick={() => handleNewsClick(item)}
            >
              <View className="news-content">
                <View className="news-header">
                  <View className="news-tags">
                    <View className="news-lang-tag">{item.lang === 'zh' ? '中文' : 'EN'}</View>
                    <View className="news-category-tag">{item.category}</View>
                  </View>
                  <View className={`news-grade grade-${item.quality?.grade?.toLowerCase() || 'd'}`}>
                    {item.quality?.grade || 'D'} {item.quality?.total_100 || 0}分
                  </View>
                </View>
                <Text className="news-title">{getDisplayTitle(item)}</Text>
                <Text className="news-summary">{item.summary_zh?.slice(0, 100)}...</Text>
                <View className="news-meta">
                  <Text className="news-source">{getDisplaySource(item)}</Text>
                  <Text className="news-date">{item.published_at?.slice(0, 10)}</Text>
                </View>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  )
}
