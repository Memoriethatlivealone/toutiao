<template>
  <div class="my-container">
    <!-- 顶部红色渐变头部：头像 + 昵称 + 简介 -->
    <div class="profile-header" @click="goToProfile">
      <div class="avatar-box">
        <van-image round width="64" height="64" :src="avatarUrl" />
      </div>
      <div class="user-meta">
        <div class="nickname">{{ isLogin ? displayName : $t('my.notLoggedIn') }}</div>
        <div class="bio" v-if="isLogin">{{ userBio }}</div>
        <div class="login-actions" v-else>
          <span class="login-btn" @click.stop="goToLogin">{{ $t('my.goToLogin') }}</span>
          <span class="register-btn" @click.stop="goToRegister">{{ $t('my.goToRegister') }}</span>
        </div>
      </div>
      <van-icon v-if="isLogin" name="arrow" class="header-arrow" />
      <!-- 桌面端没有底部 TabBar，这里提供回首页入口（手机端隐藏） -->
      <van-icon name="home-o" class="header-home" @click.stop="router.push('/home')" />
    </div>

    <!-- 功能宫格 -->
    <div class="quick-grid">
      <div class="grid-item" @click="goToFavorite">
        <van-icon name="star-o" class="grid-icon" />
        <span>{{ $t('my.myFavorite') }}</span>
      </div>
      <div class="grid-item" @click="goToHistory">
        <van-icon name="clock-o" class="grid-icon" />
        <span>{{ $t('my.browsingHistory') }}</span>
      </div>
      <div class="grid-item" @click="goToNotification">
        <van-icon name="bell" class="grid-icon" />
        <span>{{ $t('my.notifications') }}</span>
      </div>
      <div class="grid-item" @click="goToSettings">
        <van-icon name="setting-o" class="grid-icon" />
        <span>{{ $t('my.settings') }}</span>
      </div>
    </div>

    <!-- 退出登录独立卡片 -->
    <van-cell-group v-if="isLogin" inset class="logout-group">
      <van-cell :title="$t('my.logout')" class="logout-cell" @click="handleLogout" />
    </van-cell-group>

    <tab-bar />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { useRouter } from 'vue-router';
import { showDialog, showToast } from 'vant';
import TabBar from '../components/TabBar.vue';
import { useI18n } from 'vue-i18n';
import { apiConfig } from '../config/api';

const userStore = useUserStore();
const router = useRouter();
const { t } = useI18n();

// 没设置头像时显示的默认图
const DEFAULT_AVATAR = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

// 从store获取用户信息和登录状态
const userInfo = computed(() => userStore.userInfo);
const isLogin = computed(() => userStore.getLoginStatus);
const userBio = computed(() => userStore.getUserBio || t('profile.bio'));

// 优先显示昵称，没设置昵称时退回用户名
const displayName = computed(() => {
  const info = userInfo.value;
  return info?.nickname || info?.username || '';
});

// 后端存的是相对路径（/static/avatars/xxx.png），显示时要拼上后端地址
const avatarUrl = computed(() => {
  const avatar = userInfo.value?.avatar;
  if (!avatar) return DEFAULT_AVATAR;
  return avatar.startsWith('http') ? avatar : `${apiConfig.baseURL}${avatar}`;
});

// 跳转到登录页
const goToLogin = () => {
  router.push('/login');
};

// 跳转到注册页
const goToRegister = () => {
  router.push('/register');
};

// 跳转到个人信息页
const goToProfile = () => {
  if (isLogin.value) {
    router.push('/profile');
  }
};

// 跳转到浏览历史页面
const goToHistory = () => {
  if (isLogin.value) {
    router.push('/history');
  } else {
    showToast(t('common.login'));
    router.push('/login');
  }
};

// 跳转到我的收藏页面
const goToFavorite = () => {
  if (isLogin.value) {
    router.push('/favorite');
  } else {
    showToast(t('common.login'));
    router.push('/login');
  }
};

// 跳转到设置页面
const goToSettings = () => {
  router.push('/settings');
};

// 退出登录
const handleLogout = () => {
  showDialog({
    title: t('common.confirm'),
    message: t('my.logout') + '?',
    showCancelButton: true,
  }).then(async (action) => {
    if (action === 'confirm') {
      // 调后端删 token，本地状态在 logoutApi 里统一清理
      await userStore.logoutApi();
      router.push('/login');
    }
  });
};

// 跳转通知设置
const goToNotification = () => {
  router.push('/settings/notification');
};

// 获取用户信息
onMounted(async () => {
  try {
    await userStore.getUserInfoDetail();
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
});
</script>

<style scoped>
.my-container {
  padding-bottom: 50px;
  background-color: var(--background-color);
  color: var(--text-color);
  min-height: 100vh;
  box-sizing: border-box;
}

/* ---------------- 顶部渐变头部 ---------------- */
.profile-header {
  position: relative;
  display: flex;
  align-items: center;
  padding: 36px 20px 32px;
  background: linear-gradient(135deg, #f04142 0%, #ff6b6b 100%);
  color: #fff;
  cursor: pointer;
}

.avatar-box {
  flex-shrink: 0;
  margin-right: 14px;
}

.avatar-box :deep(.van-image) {
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.user-meta {
  flex: 1;
  min-width: 0;
}

.nickname {
  font-size: 20px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bio {
  margin-top: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.82);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-arrow {
  flex-shrink: 0;
  margin-left: 8px;
  color: rgba(255, 255, 255, 0.7);
}

/* 回首页入口只在桌面端显示，手机端用底部 TabBar */
.header-home {
  position: absolute;
  top: 14px;
  right: 16px;
  display: none;
  font-size: 20px;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  transition: color 0.2s ease;
}

.header-home:hover {
  color: #fff;
}

.login-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.login-btn,
.register-btn {
  padding: 4px 14px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1.4;
}

.login-btn {
  background-color: #fff;
  color: var(--primary-color, #f04142);
}

.register-btn {
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.7);
}

/* ---------------- 功能宫格 ---------------- */
/* 上移压在渐变头部下沿，形成浮在头部的卡片效果 */
.quick-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  margin: -16px 12px 0;
  padding: 18px 0;
  background-color: var(--card-color, #fff);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-color-light, #71717a);
  cursor: pointer;
}

.grid-item:active {
  opacity: 0.7;
}

.grid-icon {
  font-size: 24px;
  color: var(--primary-color, #f04142);
}

/* ---------------- 退出登录 ---------------- */
.logout-group {
  margin-top: 12px;
}

:deep(.logout-cell) {
  justify-content: center;
}

:deep(.logout-cell .van-cell__title) {
  flex: none;
  text-align: center;
  font-size: 15px;
  color: var(--primary-color, #f04142);
}

/* 桌面端：内容居中在 1080px 内，底部没有 tabbar 也不用留白 */
@media (min-width: 900px) {
  .my-container {
    max-width: 1080px;
    margin: 0 auto;
    padding-bottom: 40px;
  }

  .profile-header {
    margin-top: 24px;
    border-radius: 12px;
    padding: 40px 32px;
  }

  .header-home {
    display: block;
  }
}
</style>