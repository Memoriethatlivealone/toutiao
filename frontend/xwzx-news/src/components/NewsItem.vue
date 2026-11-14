<template>
  <!-- 今日头条风格新闻卡片：左侧标题 + 元信息，右侧缩略图 -->
  <div class="news-item" @click="goToDetail">
    <div class="news-content">
      <h3 class="news-title">{{ news.title }}</h3>
      <div class="news-info">
        <span class="news-author">{{ news.author }}</span>
        <span class="news-time">{{ formatTime(news.publishTime) }}</span>
        <span class="news-views">{{ formatViews(news.views) }}阅读</span>
      </div>
    </div>
    <div class="news-image" v-if="news.image">
      <img :src="news.image" :alt="news.title" loading="lazy">
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  news: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const goToDetail = () => {
  router.push(`/news/detail/${props.news.id}`)
}

// 后端返回的时间可能是 ISO 格式（2024-01-01T08:00:00），
// 列表里只展示到分钟，并去掉中间的 T
const formatTime = (value) => {
  if (!value) return ''
  return String(value).replace('T', ' ').slice(0, 16)
}

// 阅读量超过一万时显示「1.2万」，与新闻类 App 的习惯一致
const formatViews = (value) => {
  const count = Number(value) || 0
  return count >= 10000 ? `${(count / 10000).toFixed(1)}万` : String(count)
}
</script>

<style scoped>
.news-item {
  display: flex;
  align-items: stretch;
  gap: 12px;
  padding: 14px 16px;
  background-color: var(--card-color, #fff);
  border-bottom: 1px solid var(--border-color, #ededed);
  cursor: pointer;
  transition: background-color 0.15s ease;
}

/* 按下时轻微反馈，接近原生 App 的手感 */
.news-item:active {
  background-color: #f7f7f8;
}

.news-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.news-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  line-height: 1.45;
  color: var(--text-color, #1a1a1a);
  word-break: break-word;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.news-info {
  display: flex;
  align-items: center;
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-color-lighter, #a1a1aa);
  white-space: nowrap;
  overflow: hidden;
}

/* 元信息之间用小圆点分隔，第一项前面不加 */
.news-info span + span::before {
  content: '·';
  margin: 0 6px;
  color: #d4d4d8;
}

.news-author {
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 90px;
}

.news-image {
  width: 112px;
  height: 76px;
  flex-shrink: 0;
  align-self: center;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
  background-color: #f0f0f0;
}

/* 桌面端：更大的标题和缩略图，悬停时整行高亮 */
@media (min-width: 900px) {
  .news-item {
    gap: 20px;
    padding: 16px 20px;
  }

  .news-item:hover {
    background-color: #fafafa;
  }

  .news-title {
    font-size: 17px;
  }

  .news-image {
    width: 144px;
    height: 92px;
  }

  .news-info {
    margin-top: 10px;
    font-size: 13px;
  }
}
</style>