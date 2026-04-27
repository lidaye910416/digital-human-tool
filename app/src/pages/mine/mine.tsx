import { View, Text } from '@tarojs/components'
import './mine.scss'

export default function Mine() {
  return (
    <View className="mine-page">
      {/* 用户信息 */}
      <View className="user-info">
        <View className="avatar">
          <Text className="avatar-icon">👤</Text>
        </View>
        <Text className="username">Tech Echo 用户</Text>
        <Text className="user-hint">科技资讯，有声播报</Text>
      </View>

      {/* 功能列表 */}
      <View className="menu-list">
        <View className="menu-item">
          <Text className="menu-icon">📊</Text>
          <Text className="menu-text">我的收藏</Text>
          <Text className="menu-arrow">→</Text>
        </View>
        <View className="menu-item">
          <Text className="menu-icon">⏰</Text>
          <Text className="menu-text">播放历史</Text>
          <Text className="menu-arrow">→</Text>
        </View>
        <View className="menu-item">
          <Text className="menu-icon">⚙️</Text>
          <Text className="menu-text">设置</Text>
          <Text className="menu-arrow">→</Text>
        </View>
        <View className="menu-item">
          <Text className="menu-icon">❓</Text>
          <Text className="menu-text">帮助与反馈</Text>
          <Text className="menu-arrow">→</Text>
        </View>
      </View>

      {/* 关于 */}
      <View className="about">
        <Text className="about-title">Tech Echo</Text>
        <Text className="about-version">Version 0.2.0</Text>
        <Text className="about-desc">科技资讯播报平台</Text>
      </View>
    </View>
  )
}
