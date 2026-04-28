import { Component } from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

export default class Category extends Component {
  componentDidMount() {}

  render() {
    return (
      <View className="category">
        <Text>Tech Echo - 分类</Text>
      </View>
    )
  }
}
