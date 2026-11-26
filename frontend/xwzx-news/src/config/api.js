/**
 * API配置文件
 * 包含 API 基础 URL 和 AI 问答接口地址
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}

// AI 问答统一走本地后端，密钥保存在后端 .env，前端不再持有 API Key
export const aiChatConfig = {
  apiEndpoint: `${apiConfig.baseURL}/api/ai/chat`,
}
