<template>
  <div class="home-page">
    <!-- ==================== 顶部深色 Hero 区 ==================== -->
    <header class="hero">
      <!-- 底层星空：CSS 星点，地球之外的部分会露出来 -->
      <div class="hero-stars"></div>
      <!-- WebGL 实时渲染的地球：自转 + 昼夜 + 城市灯光 + 大气辉光 -->
      <earth-hero />

      <div class="hero-topbar">
        <div class="topbar-left">
          <span class="top-link" @click="showToast('请使用手机浏览器打开')">下载头条APP</span>
          <span class="top-link" @click="showToast('请使用浏览器菜单添加到桌面')">添加到桌面</span>
          <span class="top-link" @click="router.push('/settings/about')">关于头条</span>
          <span class="top-link" @click="showToast('反馈功能开发中')">反馈</span>
        </div>
        <div class="topbar-right">
          <span class="weather">杭州 18℃</span>
          <span class="top-link" @click="goToNotification"><van-icon name="bell" /> 消息</span>
          <span class="top-link" @click="router.push('/aichat')"><van-icon name="chat-o" /> AI问答</span>
          <span class="top-link" @click="router.push('/my')"><van-icon name="user-o" /> 我的</span>
          <button v-if="!isLogin" class="top-login-btn" @click="router.push('/login')">登录</button>
          <span v-else class="top-user" @click="router.push('/my')">{{ displayName }}</span>
        </div>
      </div>

      <div class="hero-inner">
        <h1 class="hero-title">今日头条</h1>
        <div class="hero-search">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索感兴趣的内容"
            @keyup.enter="handleSearch"
          />
          <van-icon name="search" class="search-icon" @click="handleSearch" />
        </div>
      </div>
    </header>

    <!-- ==================== 频道导航 ==================== -->
    <nav class="channel-nav">
      <div class="channel-inner">
        <span
          v-for="(category, index) in displayCategories"
          :key="category.id"
          class="channel"
          :class="{ active: activeTab === index }"
          @click="activeTab = index"
        >
          {{ getCategoryTranslation(category.name) }}
        </span>
        <span class="channel channel-more" @click="router.push('/category')">
          更多 <van-icon name="arrow-down" />
        </span>
      </div>
    </nav>

    <!-- ==================== 主体：新闻列表 + 右侧栏 ==================== -->
    <div class="page-body">
      <main class="news-column">
        <div v-if="appliedKeyword" class="search-result-bar">
          <span>搜索「{{ appliedKeyword }}」· 共 {{ filteredNews.length }} 条结果</span>
          <span class="clear-search" @click="clearSearch">清除搜索</span>
        </div>

        <van-pull-refresh v-model="newsStore.refreshing" @refresh="onRefresh">
          <van-list
            v-model:loading="newsStore.loading"
            :finished="appliedKeyword ? true : newsStore.finished"
            :immediate-check="false"
            :finished-text="appliedKeyword ? '' : $t('home.noMore')"
            @load="onLoad"
          >
            <news-item
              v-for="item in filteredNews"
              :key="item.id"
              :news="item"
            />
          </van-list>
          <van-empty
            v-if="appliedKeyword && !filteredNews.length && !newsStore.loading"
            description="没有找到相关新闻"
          />
        </van-pull-refresh>
      </main>

      <aside class="sidebar">
        <!-- 登录卡片 -->
        <div class="side-card login-card">
          <span class="login-card-text">
            {{ isLogin ? `欢迎回来，${displayName}` : '登录后，头条更懂你' }}
          </span>
          <button class="login-card-btn" @click="router.push(isLogin ? '/my' : '/login')">
            {{ isLogin ? '个人中心' : '立即登录' }}
          </button>
        </div>

        <!-- 安全课堂 -->
        <div class="side-card">
          <div class="side-head">
            <span class="side-title"><van-icon name="shield-o" /> 安全课堂</span>
          </div>
          <div class="safety-grid">
            <div class="safety-card safety-red" @click="showToast('安全课堂内容整理中')">
              <span class="safety-tag">头条安全月报</span>
              <span class="safety-name">头条反诈指南</span>
            </div>
            <div class="safety-card safety-gold" @click="showToast('安全课堂内容整理中')">
              <span class="safety-tag">头条安全月报</span>
              <span class="safety-name">内容审核规范</span>
            </div>
          </div>
        </div>

        <!-- 头条热榜 -->
        <div class="side-card">
          <div class="side-head">
            <span class="side-title"><van-icon name="fire-o" /> 头条热榜</span>
            <span class="side-more" @click="refreshHot">
              <van-icon name="replay" /> 换一换
            </span>
          </div>
          <ol class="hot-list">
            <li
              v-for="(item, index) in hotList"
              :key="item.id"
              @click="goToDetail(item.id)"
            >
              <span class="hot-rank" :class="{ top: index < 3 }">{{ index + 1 }}</span>
              <span class="hot-title">{{ item.title }}</span>
              <span v-if="index < 2" class="hot-badge">热</span>
            </li>
            <li v-if="!hotList.length" class="hot-empty">暂无热榜数据</li>
          </ol>
        </div>
      </aside>
    </div>

    <!-- ==================== 页脚 ==================== -->
    <footer class="site-footer">
      <div class="footer-links">
        <span @click="showToast('感谢关注')">加入头条</span>
        <span @click="showToast('用户协议整理中')">用户协议</span>
        <span @click="router.push('/settings/privacy')">隐私政策</span>
        <span @click="showToast('媒体合作请联系管理员')">媒体合作</span>
        <span @click="showToast('广告合作请联系管理员')">广告合作</span>
        <span @click="showToast('友情链接整理中')">友情链接</span>
        <span @click="router.push('/category')">更多</span>
        <span @click="showToast('请使用手机浏览器打开')">下载今日头条APP</span>
      </div>
      <div class="footer-copy">© 2026 新闻资讯 · 学习演示项目，仅供交流使用</div>
    </footer>

    <!-- 只在移动端显示 -->
    <tab-bar />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, defineAsyncComponent } from 'vue'
import { useNewsStore } from '../store/modules/news'
import { useUserStore } from '../store/user'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import NewsItem from '../components/NewsItem.vue'
import TabBar from '../components/TabBar.vue'

// three.js 体积较大，异步加载：不阻塞首屏，地球加载完成后再叠加显示
const EarthHero = defineAsyncComponent(() => import('../components/EarthHero.vue'))

const newsStore = useNewsStore()
const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()

const activeTab = ref(0)
const searchKeyword = ref('')
// 按下回车后才生效的搜索词，避免边输入边过滤造成列表跳动
const appliedKeyword = ref('')
// 热榜「换一换」的起始位置
const hotOffset = ref(0)

const isLogin = computed(() => userStore.getLoginStatus)
const displayName = computed(
  () => userStore.userInfo?.nickname || userStore.userInfo?.username || ''
)

// 频道栏不包含「更多」这个假分类
const displayCategories = computed(() =>
  newsStore.categories.filter((category) => category.name !== '更多')
)

// 搜索时在前端过滤已加载的新闻；未搜索时展示正常列表
const filteredNews = computed(() => {
  if (!appliedKeyword.value) return newsStore.newsList
  const keyword = appliedKeyword.value.toLowerCase()
  return newsStore.newsList.filter((item) =>
    (item.title || '').toLowerCase().includes(keyword)
  )
})

// 热榜取当前分类新闻的前 5 条，「换一换」时向后错位
const hotList = computed(() => {
  const source = newsStore.newsList.filter((item) => item.title)
  if (!source.length) return []
  const size = Math.min(5, source.length)
  const start = hotOffset.value % source.length
  return Array.from({ length: size }, (_, i) => source[(start + i) % source.length])
})

const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  appliedKeyword.value = keyword
  if (keyword) {
    showToast(`为你找到 ${filteredNews.value.length} 条相关新闻`)
  }
}

const clearSearch = () => {
  searchKeyword.value = ''
  appliedKeyword.value = ''
}

const refreshHot = () => {
  hotOffset.value += 5
}

const goToDetail = (id) => {
  router.push(`/news/detail/${id}`)
}

const goToNotification = () => {
  if (isLogin.value) {
    router.push('/settings/notification')
  } else {
    router.push('/login')
  }
}

// 分类名 → i18n key
const getCategoryTranslation = (categoryName) => {
  const categoryMap = {
    '头条': 'headline',
    '社会': 'society',
    '国内': 'domestic',
    '国际': 'international',
    '娱乐': 'entertainment',
    '体育': 'sports',
    '军事': 'military',
    '科技': 'technology',
    '财经': 'finance',
    '更多': 'more'
  }
  const key = categoryMap[categoryName]
  return key ? t(`home.categories.${key}`) : categoryName
}

onMounted(async () => {
  await newsStore.getCategories()

  // 从分类页跳回来时带 categoryId，定位到对应频道
  const categoryId = Number(route.query.categoryId)
  if (categoryId) {
    const index = displayCategories.value.findIndex((cat) => cat.id === categoryId)
    if (index !== -1) {
      activeTab.value = index
      // 先同步 store 的当前分类，避免下面重复请求一次
      newsStore.currentCategory = categoryId
    }
  }

  newsStore.getNewsList()
})

// 点击频道时切换分类
watch(activeTab, (newIndex) => {
  const category = displayCategories.value[newIndex]
  if (category) {
    hotOffset.value = 0
    newsStore.changeCategory(category.id)
  }
})

// 路由上带 categoryId 时（比如从分类页返回）同步频道
watch(
  () => route.query.categoryId,
  (newCategoryId) => {
    if (!newCategoryId) return
    const index = displayCategories.value.findIndex(
      (cat) => cat.id === Number(newCategoryId)
    )
    if (index !== -1) activeTab.value = index
  }
)

const onRefresh = () => {
  newsStore.getNewsList(true)
}

const onLoad = () => {
  // 搜索模式下不再加载更多
  if (appliedKeyword.value) return
  newsStore.getNewsList()
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: var(--background-color, #f5f6f7);
}

/* ==================== Hero 区 ==================== */
/* 背景由 EarthHero 组件用 WebGL 实时渲染（地球自转 + 星空） */
.hero {
  position: relative;
  height: 460px;
  overflow: hidden;
  background-color: #05070f;
  color: #fff;
}

/* 星空：多重 radial-gradient 画出来的星点，垫在地球画布下面 */
.hero-stars {
  position: absolute;
  inset: 0;
  z-index: 0;
  background-image:
    radial-gradient(1.5px 1.5px at 4% 20%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 9% 52%, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(1.5px 1.5px at 16% 32%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 22% 68%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 31% 15%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1.5px 1.5px at 38% 44%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 47% 10%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 58% 27%, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(1.5px 1.5px at 66% 58%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 73% 20%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1.5px 1.5px at 81% 47%, rgba(255, 255, 255, 0.6), transparent),
    radial-gradient(1px 1px at 88% 12%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 93% 36%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 97% 62%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1.5px 1.5px at 52% 38%, rgba(180, 210, 255, 0.6), transparent);
  pointer-events: none;
}

.hero-topbar {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 18px 32px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.72);
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
}

.topbar-left {
  gap: 28px;
}

.topbar-right {
  gap: 22px;
}

.top-link,
.weather,
.top-user {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.top-link:hover,
.top-user:hover {
  color: #fff;
}

.top-user {
  font-weight: 500;
  color: #fff;
}

.topbar-right .van-icon {
  font-size: 15px;
}

.top-login-btn {
  padding: 7px 22px;
  border: none;
  border-radius: 4px;
  background-color: var(--primary-color, #f04142);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.top-login-btn:hover {
  background-color: #d93638;
}

.hero-inner {
  position: relative;
  z-index: 2;
  max-width: 700px;
  margin: 0 auto;
  padding: 36px 24px 0;
  text-align: center;
}

.hero-title {
  margin: 0 0 28px;
  font-size: 46px;
  font-weight: 700;
  letter-spacing: 4px;
  color: #fff;
  text-shadow: 0 4px 32px rgba(0, 0, 0, 0.5), 0 2px 10px rgba(0, 0, 0, 0.35);
}

.hero-search {
  display: flex;
  align-items: center;
  height: 50px;
  padding: 0 20px;
  background-color: rgba(255, 255, 255, 0.96);
  border-radius: 8px;
  box-shadow: 0 10px 36px rgba(0, 0, 0, 0.28);
}

.hero-search input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: #333;
}

.hero-search input::placeholder {
  color: #a1a1aa;
}

.search-icon {
  flex-shrink: 0;
  margin-left: 12px;
  font-size: 20px;
  color: var(--primary-color, #f04142);
  cursor: pointer;
}

/* ==================== 频道导航 ==================== */
.channel-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #fff;
  border-bottom: 1px solid var(--border-color, #ededed);
}

.channel-inner {
  display: flex;
  align-items: center;
  gap: 36px;
  max-width: 1200px;
  height: 56px;
  margin: 0 auto;
  padding: 0 24px;
  overflow-x: auto;
}

.channel {
  position: relative;
  flex-shrink: 0;
  font-size: 16px;
  line-height: 56px;
  color: #444;
  white-space: nowrap;
  cursor: pointer;
  transition: color 0.2s ease;
}

.channel:hover {
  color: var(--primary-color, #f04142);
}

.channel.active {
  color: var(--primary-color, #f04142);
  font-weight: 600;
}

.channel.active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 8px;
  width: 24px;
  height: 3px;
  border-radius: 2px;
  background-color: var(--primary-color, #f04142);
  transform: translateX(-50%);
}

.channel-more {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-color-light, #71717a);
  font-size: 15px;
}

/* ==================== 主体布局 ==================== */
.page-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  align-items: start;
  max-width: 1200px;
  margin: 20px auto 0;
  padding: 0 24px 48px;
}

.news-column {
  min-height: 600px;
  background-color: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.search-result-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 20px;
  background-color: #fff8f8;
  border-bottom: 1px solid #ffe3e3;
  font-size: 14px;
  color: var(--text-color-light, #71717a);
}

.clear-search {
  flex-shrink: 0;
  color: var(--primary-color, #f04142);
  cursor: pointer;
}

/* ==================== 右侧栏 ==================== */
.sidebar {
  position: sticky;
  top: 76px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.side-card {
  padding: 16px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.login-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 20px 16px;
}

.login-card-text {
  font-size: 15px;
  color: #444;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.login-card-btn {
  flex-shrink: 0;
  padding: 8px 18px;
  border: none;
  border-radius: 6px;
  background-color: var(--primary-color, #f04142);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.login-card-btn:hover {
  background-color: #d93638;
}

.side-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.side-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color, #1a1a1a);
}

.side-title .van-icon {
  color: var(--primary-color, #f04142);
  font-size: 17px;
}

.side-more {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: var(--text-color-lighter, #a1a1aa);
  cursor: pointer;
  transition: color 0.2s ease;
}

.side-more:hover {
  color: var(--primary-color, #f04142);
}

/* 安全课堂卡片 */
.safety-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.safety-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 80px;
  padding: 10px 12px;
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.safety-card:hover {
  transform: translateY(-2px);
}

.safety-red {
  background: linear-gradient(135deg, #e04a3a 0%, #8f1f16 100%);
}

.safety-gold {
  background: linear-gradient(135deg, #e0a83a 0%, #9a5f12 100%);
}

.safety-tag {
  align-self: flex-start;
  padding: 2px 6px;
  border-radius: 3px;
  background-color: rgba(255, 255, 255, 0.22);
  font-size: 11px;
}

.safety-name {
  font-size: 15px;
  font-weight: 600;
}

/* 热榜 */
.hot-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.hot-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 9px 0;
  cursor: pointer;
}

.hot-rank {
  flex-shrink: 0;
  width: 18px;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-color-lighter, #a1a1aa);
  text-align: center;
}

.hot-rank.top {
  color: var(--primary-color, #f04142);
}

.hot-title {
  flex: 1;
  font-size: 14px;
  line-height: 1.45;
  color: #262626;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  transition: color 0.2s ease;
}

.hot-list li:hover .hot-title {
  color: var(--primary-color, #f04142);
}

.hot-badge {
  flex-shrink: 0;
  margin-top: 1px;
  padding: 1px 4px;
  border-radius: 3px;
  background-color: var(--primary-color, #f04142);
  font-size: 10px;
  color: #fff;
}

.hot-empty {
  font-size: 13px;
  color: var(--text-color-lighter, #a1a1aa);
  cursor: default;
}

/* ==================== 页脚 ==================== */
.site-footer {
  padding: 24px;
  background-color: #fafafa;
  border-top: 1px solid var(--border-color, #ededed);
  text-align: center;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px 20px;
  margin-bottom: 10px;
  font-size: 13px;
  color: var(--text-color-light, #71717a);
}

.footer-links span {
  cursor: pointer;
  transition: color 0.2s ease;
}

.footer-links span:hover {
  color: var(--primary-color, #f04142);
}

.footer-copy {
  font-size: 12px;
  color: var(--text-color-lighter, #a1a1aa);
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .page-body {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }
}

@media (max-width: 768px) {
  .hero {
    height: 300px;
  }

  .hero-topbar {
    padding: 12px 16px;
  }

  .topbar-left {
    display: none;
  }

  .topbar-right {
    gap: 14px;
    width: 100%;
    justify-content: flex-end;
  }

  .weather {
    display: none;
  }

  .hero-inner {
    padding: 18px 16px 0;
  }

  .hero-title {
    margin-bottom: 18px;
    font-size: 32px;
  }

  .hero-search {
    height: 42px;
    padding: 0 14px;
  }

  .channel-inner {
    gap: 24px;
    height: 48px;
    padding: 0 12px;
  }

  .channel {
    font-size: 15px;
    line-height: 48px;
  }

  .page-body {
    gap: 12px;
    margin-top: 12px;
    padding: 0 12px 70px;
  }

  .news-column {
    border-radius: 8px;
  }

  .sidebar {
    gap: 12px;
  }

  .site-footer {
    padding-bottom: 70px;
  }
}
</style>