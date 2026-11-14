<template>
  <div class="news-detail">
    <van-nav-bar
      title="新闻详情"
      left-arrow
      @click-left="onClickLeft"
      fixed
      :border="false"
    />

    <div class="detail-content" v-if="newsStore.newsDetail.id">
      <div class="title-container">
        <h1 class="title">{{ newsStore.newsDetail.title }}</h1>
        <van-button
          class="favorite-btn"
          :icon="isFavorite ? 'star' : 'star-o'"
          :class="{ 'is-favorite': isFavorite }"
          :border="false"
          @click="toggleFavorite"
        />
      </div>

      <div class="info">
        <span>{{ newsStore.newsDetail.author }}</span>
        <span>{{ formatTime(newsStore.newsDetail.publishTime) }}</span>
        <span>{{ formatViews(newsStore.newsDetail.views) }}阅读</span>
      </div>
      
      <div class="cover" v-if="newsStore.newsDetail.image">
        <img :src="newsStore.newsDetail.image" :alt="newsStore.newsDetail.title">
      </div>
      
      <div class="content">
        <p v-for="(paragraph, index) in contentParagraphs" :key="index">
          {{ paragraph }}
        </p>
      </div>
      
      <div class="related-news" v-if="newsStore.newsDetail.relatedNews?.length">
        <h3>相关推荐</h3>
        <div class="related-list">
          <div 
            class="related-item" 
            v-for="item in newsStore.newsDetail.relatedNews" 
            :key="item.id"
            @click="goToRelatedNews(item.id)"
          >
            <div class="related-image">
              <img :src="item.image" :alt="item.title">
            </div>
            <div class="related-title">{{ item.title }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <van-empty v-else description="加载中..." />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNewsStore } from '../store/modules/news'
import { useHistoryStore } from '../store/modules/history'
import { useFavoriteStore } from '../store/modules/favorite'
import { useUserStore } from '../store/user'
import { showToast } from 'vant'

const route = useRoute()
const router = useRouter()
const newsStore = useNewsStore()
const historyStore = useHistoryStore()
const favoriteStore = useFavoriteStore()
const userStore = useUserStore()

// 获取路由参数中的新闻ID
const newsId = computed(() => Number(route.params.id))

// 将内容拆分为段落
const contentParagraphs = computed(() => {
  if (!newsStore.newsDetail.content) return []
  return newsStore.newsDetail.content.split('\n\n').filter(p => p.trim())
})

// 返回上一页
const onClickLeft = () => {
  router.back()
}

// 后端时间可能是 ISO 格式（2024-01-01T08:00:00），展示时去掉 T 并截到分钟
const formatTime = (value) => {
  if (!value) return ''
  return String(value).replace('T', ' ').slice(0, 16)
}

// 阅读量超过一万时显示「1.2万」
const formatViews = (value) => {
  const count = Number(value) || 0
  return count >= 10000 ? `${(count / 10000).toFixed(1)}万` : String(count)
}

// 跳转到相关新闻
const goToRelatedNews = (id) => {
  router.push(`/news/detail/${id}`)
}

// 判断当前新闻是否已收藏
const isFavorite = computed(() => {
  return favoriteStore.isFavorite(newsId.value)
})

// 切换收藏状态
const toggleFavorite = async () => {
  // 判断用户是否已登录
  if (!userStore.getLoginStatus) {
    // 未登录则跳转到登录页
    showToast({
      message: '请先登录后再收藏',
      position: 'bottom',
    })
    router.push('/login')
    return
  }
  
  // 已登录则调用API切换收藏状态
  const status = await favoriteStore.toggleFavorite(newsStore.newsDetail)
  
  if (status === true) {
    showToast({
      message: '已添加到收藏',
      position: 'bottom',
    })
  } else if (status === false) {
    showToast({
      message: '已取消收藏',
      position: 'bottom',
    })
  } else {
    // status为null表示操作失败
    showToast({
      message: '操作失败，请稍后重试',
      position: 'bottom',
    })
  }
}

// 组件挂载时获取新闻详情并添加到浏览历史
onMounted(async () => {
  await newsStore.getNewsDetail(newsId.value)
  
  // 添加到浏览历史
  if (newsStore.newsDetail.id) {
    // 先调用API记录浏览历史
    if (userStore.getLoginStatus) {
      try {
        const result = await historyStore.addHistoryApi(newsStore.newsDetail.id);
        console.log('记录浏览历史API结果:', result);
      } catch (error) {
        console.error('记录浏览历史API失败:', error);
      }
    }
    
    // 无论API是否成功，都添加到本地浏览历史
    // historyStore.addHistory(newsStore.newsDetail);
  }
  
  // 加载收藏数据
  favoriteStore.loadFavorites()
  
  // 检查文章收藏状态
  if (userStore.getLoginStatus && newsStore.newsDetail.id) {
    const result = await favoriteStore.checkFavoriteStatusApi(newsStore.newsDetail.id)
    if (result.success && !result.isLocal) {
      // 如果API请求成功且不是本地状态，更新本地收藏状态
      if (result.isFavorite && !favoriteStore.isFavorite(newsStore.newsDetail.id)) {
        favoriteStore.addFavorite(newsStore.newsDetail)
      } else if (!result.isFavorite && favoriteStore.isFavorite(newsStore.newsDetail.id)) {
        favoriteStore.removeFavorite(newsStore.newsDetail.id)
      }
    }
  }
})
</script>

<style scoped>
.news-detail {
  padding-top: 46px;
  background-color: var(--background-color, #f5f6f7);
  min-height: 100vh;
}

/* 桌面端：正文限制在 900px 宽的白色文章区，居中显示 */
.detail-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 40px 48px;
  background-color: var(--card-color, #fff);
}

.title-container {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}

.title {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--text-color, #1a1a1a);
  margin: 0;
  flex: 1;
  word-break: break-word;
}

/* 收藏按钮：无边框的图标按钮，收藏后变成品牌红 */
.favorite-btn {
  flex-shrink: 0;
  margin-left: 10px;
  padding: 0;
  width: 40px;
  height: 40px;
  font-size: 22px;
  color: #c8c9cc;
  background-color: transparent;
}

.favorite-btn.is-favorite {
  color: var(--primary-color, #f04142);
}

.info {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--text-color-lighter, #a1a1aa);
  margin-bottom: 18px;
}

/* 元信息之间用中点分隔 */
.info span + span::before {
  content: '·';
  margin: 0 8px;
  color: #d4d4d8;
}

.cover {
  margin-bottom: 20px;
}

.cover img {
  display: block;
  width: 100%;
  border-radius: 8px;
}

.content {
  font-size: 17px;
  line-height: 1.75;
  color: #262626;
}

.content p {
  margin: 0 0 18px;
  text-align: justify;
}

/* 相关推荐：灰色底板块，和正文拉开层次 */
.related-news {
  margin: 24px -40px 0;
  padding: 24px 40px;
  background-color: var(--background-color, #f5f6f7);
}

.related-news h3 {
  position: relative;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-color, #1a1a1a);
  margin: 0 0 14px;
  padding-left: 10px;
}

.related-news h3::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 15px;
  border-radius: 2px;
  background-color: var(--primary-color, #f04142);
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.related-item {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: var(--card-color, #fff);
  border-radius: 8px;
}

.related-image {
  width: 84px;
  height: 60px;
  margin-right: 12px;
  flex-shrink: 0;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.related-title {
  font-size: 15px;
  line-height: 1.45;
  color: var(--text-color, #1a1a1a);
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 手机端恢复紧凑排版 */
@media (max-width: 768px) {
  .detail-content {
    padding: 20px 16px 32px;
  }

  .related-news {
    margin: 24px -16px 0;
    padding: 16px;
  }
}
</style>