export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/category/index',
    'pages/profile/index',
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#0a0a0a',
    navigationBarTitleText: 'Tech Echo',
    navigationBarTextStyle: 'white',
    backgroundColor: '#0a0a0a'
  },
  tabBar: {
    color: '#666666',
    selectedColor: '#00ff88',
    backgroundColor: '#0a0a0a',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页'
      },
      {
        pagePath: 'pages/category/index',
        text: '分类'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的'
      }
    ]
  },
  permission: {
    'scope.userLocation': {
      desc: '你的位置信息将用于提供更好的新闻服务'
    }
  }
})
