<template>
  <div class="sub-page">
    <van-nav-bar title="隐私设置" left-arrow @click-left="$router.back()" fixed />
    <div class="page-content">
      <van-cell-group inset title="我们收集哪些信息">
        <van-cell title="账号信息" label="用户名、加密后的密码（不存明文）、昵称、头像" />
        <van-cell title="使用记录" label="收藏的新闻、浏览历史" />
      </van-cell-group>

      <van-cell-group inset title="这些信息用来做什么">
        <van-cell title="提供核心功能" label="登录、收藏、查看浏览历史" />
        <van-cell title="改善体验" label="根据浏览记录推荐更相关的内容" />
        <van-cell title="不用于" label="广告推送、向第三方出售或共享" />
      </van-cell-group>

      <van-cell-group inset title="你的权利">
        <van-cell title="清除浏览历史" label="在「我的 - 浏览历史」里可随时清空" is-link @click="goHistory" />
        <van-cell title="清除收藏" label="在「我的 - 我的收藏」里可随时清空" is-link @click="goFavorite" />
        <van-cell title="注销账号" label="如需删除全部数据，请联系管理员" />
      </van-cell-group>

      <p class="tips">本页面仅作说明，具体的数据处理方式以实际部署环境为准。</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
const goHistory = () => router.push('/history');
const goFavorite = () => router.push('/favorite');
</script>

<style scoped>
.sub-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-top: 46px;
  padding-bottom: 20px;
}
.page-content {
  margin-top: 12px;
}
.tips {
  margin: 16px;
  font-size: 12px;
  color: #969799;
  line-height: 1.6;
}
</style>