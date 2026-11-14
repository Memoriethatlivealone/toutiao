import { defineStore } from 'pinia';

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: localStorage.getItem('theme') || 'light', // 默认浅色主题
    themes: {
      light: {
        name: '经典红',
        // 今日头条风格：浅灰背景 + 白色卡片 + 品牌红强调色
        backgroundColor: '#f5f6f7',
        textColor: '#1a1a1a',
        primaryColor: '#f04142',
        secondaryColor: '#ffffff',
      },
      dark: {
        name: '深色模式',
        backgroundColor: '#121212',
        textColor: '#ffffff',
        primaryColor: '#4c8bf5',
        secondaryColor: '#2d2d2d',
      },
      blue: {
        name: '蓝色主题',
        backgroundColor: '#e6f7ff',
        textColor: '#333333',
        primaryColor: '#1890ff',
        secondaryColor: '#bae7ff',
      },
      green: {
        name: '绿色主题',
        backgroundColor: '#f6ffed',
        textColor: '#333333',
        primaryColor: '#52c41a',
        secondaryColor: '#d9f7be',
      }
    }
  }),
  
  getters: {
    getCurrentTheme: (state) => state.currentTheme,
    getThemeConfig: (state) => state.themes[state.currentTheme],
    getAllThemes: (state) => Object.keys(state.themes).map(key => ({
      id: key,
      name: state.themes[key].name,
      primaryColor: state.themes[key].primaryColor
    }))
  },
  
  actions: {
    setTheme(themeName) {
      if (this.themes[themeName]) {
        this.currentTheme = themeName;
        localStorage.setItem('theme', themeName);
        this.applyTheme();
      }
    },
    
    applyTheme() {
      const theme = this.themes[this.currentTheme];
      document.documentElement.style.setProperty('--background-color', theme.backgroundColor);
      document.documentElement.style.setProperty('--text-color', theme.textColor);
      document.documentElement.style.setProperty('--primary-color', theme.primaryColor);
      document.documentElement.style.setProperty('--secondary-color', theme.secondaryColor);
      // 同步 Vant 的强调色变量，切换主题时按钮、TabBar、Tabs 下划线一起变色
      document.documentElement.style.setProperty('--van-primary-color', theme.primaryColor);
      document.documentElement.style.setProperty('--van-tabs-bottom-bar-color', theme.primaryColor);
      document.documentElement.style.setProperty('--van-tabbar-item-active-color', theme.primaryColor);
    },
    
    initTheme() {
      this.applyTheme();
    }
  }
});