# Apple 风格设计系统

基于 Apple 官方设计语言的 DESIGN.md 文件。

---

## 1. Visual Theme & Atmosphere

**氛围**: 极简、精致、高级感
**密度**: 大量留白，内容为王
**设计哲学**: "Design is not just what it looks like and feels like. Design is how it works."

**核心原则**:
- 内容优先，界面隐形
- 精致到像素级
- 自然、直觉的交互
- 深度与层次感

---

## 2. Color Palette

### 主色调

| 名称 | 十六进制 | 用途 |
|------|----------|------|
| Apple Blue | `#007AFF` | 主链接、主要操作 |
| Apple Green | `#34C759` | 成功、正向状态 |
| Apple Red | `#FF3B30` | 错误、删除、停止 |
| Apple Orange | `#FF9500` | 警告、注意 |
| Apple Yellow | `#FFCC00` | 提示、注意事项 |
| Apple Purple | `#AF52DE` | 特殊功能 |
| Apple Pink | `#FF2D55` | 促销、特色内容 |
| Apple Teal | `#5AC8FA` | 信息、进度 |

### 背景色

| 名称 | 十六进制 | 用途 |
|------|----------|------|
| White | `#FFFFFF` | 亮色模式背景 |
| Light Gray | `#F5F5F7` | Apple 风格浅灰背景 |
| Medium Gray | `#86868B` | 次要文字 |
| Dark Gray | `#1D1D1F` | 深色模式背景 |
| Black | `#000000` | 纯黑 (用于 OLED) |

### 文字色

| 名称 | 十六进制 | 用途 |
|------|----------|------|
| Primary Text | `#1D1D1F` | 主要文字 (亮色) |
| Secondary Text | `#86868B` | 次要文字、标签 |
| Tertiary Text | `#AEAEB2` | 禁用文字 |
| White Text | `#FFFFFF` | 深色背景上的文字 |

---

## 3. Typography

**字体家族**:
```css
font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif;
```

**SF Pro Display** - 标题
**SF Pro Text** - 正文

### 字体层级

| 元素 | 字号 | 字重 | 行高 | 字间距 |
|------|------|------|------|--------|
| Large Title | 34px | 700 | 1.2 | -0.4px |
| Title 1 | 28px | 700 | 1.2 | -0.4px |
| Title 2 | 22px | 700 | 1.25 | -0.3px |
| Title 3 | 20px | 600 | 1.25 | -0.3px |
| Headline | 17px | 600 | 1.3 | -0.2px |
| Body | 17px | 400 | 1.4 | 0 |
| Callout | 16px | 400 | 1.4 | 0 |
| Subhead | 15px | 400 | 1.35 | 0 |
| Footnote | 13px | 400 | 1.35 | -0.1px |
| Caption 1 | 12px | 400 | 1.35 | 0 |
| Caption 2 | 11px | 400 | 1.3 | 0.1px |

---

## 4. Component Stylings

### 按钮

```css
/* 主要按钮 (Filled) */
.btn-primary {
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 17px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.btn-primary:hover {
  background: #0071E3;
}

.btn-primary:active {
  background: #007AFF;
  transform: scale(0.98);
}

/* 次要按钮 (Tinted) */
.btn-secondary {
  background: rgba(0, 122, 255, 0.12);
  color: #007AFF;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 17px;
  font-weight: 500;
}

/* 圆角胶囊按钮 */
.btn-pill {
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 20px;
  font-size: 15px;
  font-weight: 500;
}

/* 图标按钮 */
.btn-icon {
  background: transparent;
  color: #007AFF;
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
```

### 卡片

```css
.card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* 大圆角卡片 (Apple News Card) */
.card-apple {
  background: white;
  border-radius: 24px;
  overflow: hidden;
}
```

### 输入框

```css
.input {
  background: #F5F5F7;
  border: none;
  border-radius: 12px;
  padding: 14px 18px;
  font-size: 17px;
  color: #1D1D1F;
  transition: all 0.2s;
}

.input:focus {
  background: white;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.3);
  outline: none;
}

.input::placeholder {
  color: #86868B;
}

/* 搜索框 */
.search-input {
  background: #F5F5F7;
  border-radius: 10px;
  padding: 10px 16px 10px 40px;
  background-image: url("data:image/svg+xml,...search-icon...");
  background-repeat: no-repeat;
  background-position: 14px center;
}
```

### 标签/徽章

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

.badge-blue {
  background: rgba(0, 122, 255, 0.12);
  color: #007AFF;
}

.badge-green {
  background: rgba(52, 199, 89, 0.15);
  color: #34C759;
}

.badge-red {
  background: rgba(255, 59, 48, 0.12);
  color: #FF3B30;
}
```

### 开关 (Toggle)

```css
.toggle {
  width: 51px;
  height: 31px;
  background: #E9E9EB;
  border-radius: 16px;
  position: relative;
  cursor: pointer;
  transition: background 0.3s;
}

.toggle.active {
  background: #34C759;
}

.toggle::after {
  content: '';
  position: absolute;
  width: 27px;
  height: 27px;
  background: white;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle.active::after {
  transform: translateX(20px);
}
```

---

## 5. Layout Principles

### 间距系统 (8pt Grid)

| 名称 | 值 |
|------|-----|
| 0 | 0px |
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 32px |
| 2xl | 48px |
| 3xl | 64px |
| 4xl | 96px |

### 圆角系统

| 元素 | 圆角 |
|------|------|
| 按钮 | 12px |
| 卡片 | 20px |
| 大卡片 | 24px |
| 输入框 | 10px |
| 徽章 | 16px |
| 图片 | 12px |
| 模态框 | 24px |

### 布局特点

- **大量留白**: 内容区域周围保持充足空间
- **网格对齐**: 16px 基准网格
- **弹性布局**: 内容自适应，容器限制最大宽度
- **刘海屏适配**: 顶部安全区域 44px

---

## 6. Depth & Elevation

### 阴影层级

```css
/* 浅层阴影 (微妙) */
.shadow-sm {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* 中层阴影 (卡片) */
.shadow-md {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

/* 深层阴影 (浮层) */
.shadow-lg {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

/* 弹窗阴影 */
.shadow-modal {
  box-shadow: 0 22px 70px rgba(0, 0, 0, 0.25);
}
```

### 毛玻璃效果

```css
.glass {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
}

.glass-dark {
  background: rgba(29, 29, 31, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
}
```

---

## 7. Do's and Don'ts

### Do's
- ✅ 使用 SF Pro 字体或系统字体栈
- ✅ 保持大量留白，内容优先
- ✅ 使用圆角 12px-24px
- ✅ 微妙、柔和的阴影
- ✅ 使用毛玻璃效果增加层次
- ✅ 深浅模式保持一致的设计语言

### Don'ts
- ❌ 不要使用过于鲜艳的颜色
- ❌ 避免硬边直角
- ❌ 不要让界面过于拥挤
- ❌ 避免过度设计
- ❌ 不要忽略深色模式

---

## 8. Responsive Behavior

| 设备 | 断点 | 布局 |
|------|------|------|
| iPhone SE | < 375px | 单列，紧凑间距 |
| iPhone | 375-414px | 单列，标准间距 |
| iPad | 768-1024px | 双列，侧边导航可选 |
| Desktop | > 1024px | 多列，扩展内容区域 |

### 触摸目标
- 最小触摸区域: 44 × 44pt (iOS)
- 推荐间距: 至少 8px

---

## 9. Agent Prompt Guide

快速参考:

```
Apple 风格关键点:
- 颜色: #007AFF (蓝), #F5F5F7 (浅灰背景)
- 字体: SF Pro, -apple-system
- 圆角: 12px (按钮), 20px (卡片)
- 阴影: 柔和, 0 2-8px rgba(0,0,0,0.08)
- 留白: 大量空间
- 背景: #FFFFFF 或 #F5F5F7

当创建 Apple 风格组件时:
1. 使用 SF Pro 或系统字体
2. 大量留白，内容优先
3. 圆角 12-20px
4. 柔和阴影
5. 可选: 毛玻璃效果
6. 蓝 #007AFF 用于链接和主要操作
```
