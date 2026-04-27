import { useState, useEffect } from 'react'
import { View, Text, Audio } from '@tarojs/components'
import { getNewsDetail, readNewsAloud, markAsRead, NewsItem } from '../../api'
import './read.scss'

export default function Read() {
  const [news, setNews] = useState<NewsItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    const id = getApp().router?.params?.id
    if (id) {
      loadNews(Number(id))
    }
  }, [])

  const loadNews = async (id: number) => {
    setLoading(true)
    try {
      const res = await getNewsDetail(id)
      if (res.success) {
        setNews(res.data)
        // 标记已读
        await markAsRead(id)
      }
    } catch (e) {
      console.error('Load news failed:', e)
    }
    setLoading(false)
  }

  const handleReadAloud = async () => {
    if (!news) return

    if (audioUrl) {
      // 已有音频，切换播放状态
      setIsPlaying(!isPlaying)
      return
    }

    setIsGenerating(true)
    try {
      const res = await readNewsAloud(news.id)
      if (res.success && res.data.audio_url) {
        setAudioUrl(res.data.audio_url)
        setIsPlaying(true)
      }
    } catch (e) {
      console.error('Generate audio failed:', e)
      Taro.showToast({ title: '生成失败', icon: 'none' })
    }
    setIsGenerating(false)
  }

  const handleVideoGeneration = () => {
    Taro.showModal({
      title: '功能开发中',
      content: '数字人播报功能正在开发中，敬请期待！',
      showCancel: false
    })
  }

  if (loading) {
    return (
      <View className="read-page">
        <View className="loading">加载中...</View>
      </View>
    )
  }

  if (!news) {
    return (
      <View className="read-page">
        <View className="empty">资讯不存在</View>
      </View>
    )
  }

  return (
    <View className="read-page">
      {/* 内容区 */}
      <View className="content">
        <Text className="title">{news.title}</Text>
        <View className="meta">
          <Text className="source">{news.source_name}</Text>
          <Text className="date">{news.date_key}</Text>
        </View>
        
        {news.summary && (
          <View className="section">
            <Text className="section-title">摘要</Text>
            <Text className="section-content">{news.summary}</Text>
          </View>
        )}

        {news.content && (
          <View className="section">
            <Text className="section-title">正文</Text>
            <Text className="section-content">{news.content}</Text>
          </View>
        )}
      </View>

      {/* 底部操作栏 */}
      <View className="action-bar">
        <View className="action-item" onClick={handleReadAloud}>
          <Text className="action-icon">{audioUrl ? (isPlaying ? '⏸️' : '▶️') : '🔊'}</Text>
          <Text className="action-text">
            {isGenerating ? '生成中...' : audioUrl ? (isPlaying ? '暂停' : '朗读') : '文字转语音'}
          </Text>
        </View>

        <View className="action-item video" onClick={handleVideoGeneration}>
          <Text className="action-icon">🎬</Text>
          <Text className="action-text">数字人播报</Text>
          <Text className="action-badge">开发中</Text>
        </View>

        <View className="action-item">
          <Text className="action-icon">🔗</Text>
          <Text className="action-text">原文链接</Text>
        </View>
      </View>

      {/* 音频播放器 */}
      {audioUrl && isPlaying && (
        <Audio
          src={audioUrl}
          controls
          className="audio-player"
          onEnded={() => setIsPlaying(false)}
        />
      )}
    </View>
  )
}
