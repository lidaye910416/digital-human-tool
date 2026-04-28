import { Component } from 'react'
import { View, Text } from '@tarojs/components'
import './index.scss'

export default class Profile extends Component {
  componentDidMount() {}

  render() {
    return (
      <View className="profile">
        <Text>Tech Echo - 我的</Text>
      </View>
    )
  }
}
