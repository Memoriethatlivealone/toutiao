<template>
  <van-tabbar v-model="active" route :border="false" class="app-tabbar">
    <van-tabbar-item to="/home" icon="home-o">{{ $t('nav.home') }}</van-tabbar-item>
    <van-tabbar-item to="/aichat" icon="chat-o">{{ $t('nav.aiChat') }}</van-tabbar-item>
    <van-tabbar-item to="/my" icon="user-o">{{ $t('nav.my') }}</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

// 根据当前路由路径设置激活的标签
const setActiveTab = () => {
  const path = route.path
  if (path.includes('/home')) {
    active.value = 0
  } else if (path.includes('/aichat')) {
    active.value = 1
  } else if (path.includes('/my')) {
    active.value = 2
  }
}

// 初始化时设置激活标签
setActiveTab()
</script>

<style scoped>
/* 底部导航：白底 + 顶部细分隔线，选中项是品牌红（颜色由全局 Vant 变量控制） */
.app-tabbar {
  background-color: var(--card-color, #fff);
  border-top: 1px solid var(--border-color, #ededed);
}

:deep(.van-tabbar-item) {
  font-size: 11px;
}

:deep(.van-tabbar-item__icon) {
  font-size: 20px;
  margin-bottom: 2px;
}

/* 桌面版是网页布局，底部 tabbar 只在手机上显示 */
@media (min-width: 900px) {
  .app-tabbar {
    display: none;
  }
}
</style>