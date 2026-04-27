import { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import { getNewsList, getAvailableDates, getCategories, NewsItem } from '../../api'
import './index.scss'

export default function Index() {
  const [dates, setDates] = useState<string[]>([])
  const [categories, setCategories] = useState<{id: string; name: string; emoji: string}[]>([])
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDate, setSelectedDate] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      // 加载日期
      const datesRes = await getAvailableDates()
      if (datesRes.success && datesRes.data.length > 0) {
        setDates(datesRes.data)
        setSelectedDate(datesRes.data[0])
      }

      // 加载分类
      const categoriesRes = await getCategories()
      if (categoriesRes.success) {
        setCategories(categoriesRes.data)
      }

      // 加载最新资讯
      const newsRes = await getNewsList({ limit: 10 })
      if (newsRes.success) {
        setNews(newsRes.data.items)
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
                <Text className="news-title">{item.title}</Text>
                <View className="news-meta">
                  <Text className="news-source">{item.source_name}</Text>
                  <Text className="news-date">{item.date_key}</Text>
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
          {categories.map(cat => (
            <View key={cat.id} className="category-item">
              <Text className="category-emoji">{cat.emoji}</Text>
              <Text className="category-name">{cat.name}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  )
}
