import { useState, useEffect } from 'react'
import { View, Text, ScrollView } from '@tarojs/components'
import { getNewsList, getAvailableDates, NewsItem } from '../../api'
import './news.scss'

export default function News() {
  const [dates, setDates] = useState<string[]>([])
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDates()
  }, [])

  useEffect(() => {
    if (selectedDate) {
      loadNews(selectedDate)
    }
  }, [selectedDate])

  const loadDates = async () => {
    try {
      const res = await getAvailableDates()
      if (res.success && res.data.length > 0) {
        setDates(res.data)
        setSelectedDate(res.data[0])
      } else {
        // 无资讯时显示今天
        const today = new Date().toISOString().split('T')[0]
        setDates([today])
        setSelectedDate(today)
      }
    } catch (e) {
      console.error('Load dates failed:', e)
    }
  }

  const loadNews = async (date: string) => {
    setLoading(true)
    try {
      const res = await getNewsList({ date, limit: 50 })
      if (res.success) {
        setNews(res.data.items)
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

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (dateStr === today.toISOString().split('T')[0]) return '今天'
    if (dateStr === yesterday.toISOString().split('T')[0]) return '昨天'
    
    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  return (
    <View className="news-page">
      {/* 日期选择 */}
      <ScrollView scrollX className="date-tabs">
        {dates.map(date => (
          <View
            key={date}
            className={`date-tab ${selectedDate === date ? 'active' : ''}`}
            onClick={() => setSelectedDate(date)}
          >
            <Text className="date-text">{formatDate(date)}</Text>
            <Text className="date-full">{date}</Text>
          </View>
        ))}
      </ScrollView>

      {/* 资讯列表 */}
      <ScrollView scrollY className="news-list">
        {loading ? (
          <View className="loading">加载中...</View>
        ) : news.length === 0 ? (
          <View className="empty">
            <Text className="empty-icon">📭</Text>
            <Text className="empty-text">暂无资讯</Text>
            <Text className="empty-hint">请选择其他日期查看</Text>
          </View>
        ) : (
          news.map(item => (
            <View
              key={item.id}
              className={`news-item ${item.is_read ? 'read' : ''}`}
              onClick={() => handleNewsClick(item)}
            >
              <View className="news-content">
                <Text className="news-title">{item.title}</Text>
                {item.summary && (
                  <Text className="news-summary">{item.summary}</Text>
                )}
                <View className="news-meta">
                  <Text className="news-source">{item.source_name}</Text>
                  <View className="news-actions">
                    <Text className="action-btn">🔊 朗读</Text>
                    <Text className="action-btn">📖 阅读</Text>
                  </View>
                </View>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  )
}
