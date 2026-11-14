<template>
  <div class="sub-page">
    <van-nav-bar title="关于我们" left-arrow @click-left="$router.back()" fixed />
    <div class="page-content">
      <div class="logo-area">
        <div class="app-logo">新</div>
        <div class="app-name">新闻资讯</div>
        <div class="app-version">版本 {{ version }}</div>
      </div>

      <van-cell-group inset>
        <van-cell title="应用简介" label="聚合新闻浏览、收藏与 AI 问答的资讯类应用" />
        <van-cell title="技术栈" value="Vue 3 + Vant + FastAPI" />
        <van-cell title="后端框架" value="FastAPI + SQLAlchemy" />
        <van-cell title="数据库" value="MySQL 8" />
      </van-cell-group>

      <van-cell-group inset title="联系我们">
        <van-cell title="反馈邮箱" value="feedback@example.com" />
        <van-cell title="开源地址" value="GitHub" is-link @click="openGithub" />
      </van-cell-group>

      <p class="tips">© 2026 新闻资讯 · 仅供学习交流使用</p>
    </div>
  </div>
</template>

<script setup>
const version = '1.0.0';

// 项目仓库地址，想换成自己的直接改这里
const REPO_URL = 'https://github.com/Memoriethatlivealone/toutiao';

const openGithub = () => {
  window.open(REPO_URL, '_blank');
};
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
.logo-area {
  text-align: center;
  padding: 28px 0 24px;
}
.app-logo {
  width: 72px;
  height: 72px;
  margin: 0 auto 12px;
  border-radius: 18px;
  background: linear-gradient(135deg, #1989fa, #39a9ff);
  color: #fff;
  font-size: 32px;
  font-weight: bold;
  line-height: 72px;
}
.app-name {
  font-size: 18px;
  font-weight: 600;
  color: #323233;
}
.app-version {
  margin-top: 6px;
  font-size: 12px;
  color: #969799;
}
.tips {
  margin: 24px 16px;
  text-align: center;
  font-size: 12px;
  color: #969799;
}
</style>