<template>
  <div class="sub-page">
    <van-nav-bar title="通知设置" left-arrow @click-left="$router.back()" fixed />
    <div class="page-content">
      <van-cell-group inset title="推送通知">
        <van-cell title="新闻推送" label="重要新闻的实时提醒">
          <template #right-icon>
            <van-switch v-model="settings.newsPush" size="20" />
          </template>
        </van-cell>
        <van-cell title="收藏更新" label="收藏的新闻有新进展时提醒">
          <template #right-icon>
            <van-switch v-model="settings.favoriteUpdate" size="20" />
          </template>
        </van-cell>
        <van-cell title="系统消息" label="账号、安全相关的通知">
          <template #right-icon>
            <van-switch v-model="settings.systemMsg" size="20" />
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset title="免打扰">
        <van-cell title="夜间免打扰" label="22:00 - 08:00 不推送">
          <template #right-icon>
            <van-switch v-model="settings.doNotDisturb" size="20" />
          </template>
        </van-cell>
      </van-cell-group>

      <div class="footer">
        <van-button type="primary" block @click="saveSettings">保存设置</van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue';
import { showSuccessToast } from 'vant';

// 通知偏好目前保存在本地（localStorage），后端暂未提供通知配置接口
const STORAGE_KEY = 'notification_settings';

const defaultSettings = {
  newsPush: true,
  favoriteUpdate: true,
  systemMsg: true,
  doNotDisturb: false
};

const settings = reactive({ ...defaultSettings });

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    try {
      Object.assign(settings, JSON.parse(saved));
    } catch (error) {
      console.error('通知设置解析失败:', error);
    }
  }
});

const saveSettings = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  showSuccessToast('设置已保存');
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
.footer {
  padding: 24px 16px;
}
</style>