/**
 * Tech Echo API 接口
 */

// 基础配置
const BASE_URL = 'http://localhost:8001'

interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
}

interface NewsItem {
  id: number
  title: string
  summary: string | null
  content: string | null
  source_name: string
  category: string
  date_key: string
  score: number
  is_read: boolean
  source_url?: string
}

interface DateItem {
  id: string
  name: string
  emoji: string
}

// 获取资讯列表
export async function getNewsList(params: {
  date?: string
  category?: string
  limit?: number
  offset?: number
}): Promise<ApiResponse<{ items: NewsItem[]; total: number }>> {
  const query = new URLSearchParams()
  if (params.date) query.set('date', params.date)
  if (params.category) query.set('category', params.category)
  if (params.limit) query.set('limit', String(params.limit))
  if (params.offset) query.set('offset', String(params.offset))

  const res = await fetch(`${BASE_URL}/api/news?${query}`)
  return res.json()
}

// 获取可用日期列表
export async function getAvailableDates(): Promise<ApiResponse<string[]>> {
  const res = await fetch(`${BASE_URL}/api/news/dates`)
  return res.json()
}

// 获取资讯详情
export async function getNewsDetail(id: number): Promise<ApiResponse<NewsItem>> {
  const res = await fetch(`${BASE_URL}/api/news/${id}`)
  return res.json()
}

// 获取分类
export async function getCategories(): Promise<ApiResponse<DateItem[]>> {
  const res = await fetch(`${BASE_URL}/api/news/categories`)
  return res.json()
}

// 朗读资讯
export async function readNewsAloud(
  id: number,
  voiceId: string = 'female-tianmei'
): Promise<ApiResponse<{ audio_url: string }>> {
  const res = await fetch(
    `${BASE_URL}/api/news/${id}/read?voice_id=${voiceId}`,
    { method: 'POST' }
  )
  return res.json()
}

// 标记已读
export async function markAsRead(id: number): Promise<ApiResponse> {
  const res = await fetch(`${BASE_URL}/api/news/${id}/read`, {
    method: 'PUT'
  })
  return res.json()
}

// 手动触发收集
export async function triggerCollect(targetDate?: string): Promise<ApiResponse> {
  const res = await fetch(`${BASE_URL}/api/news/collect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_date: targetDate })
  })
  return res.json()
}

export type { NewsItem, DateItem }
