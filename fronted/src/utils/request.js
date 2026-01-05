import axios from 'axios'
import { useToastStore } from '@/store/toast'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 120000, // 增加到120秒，因为AI规划接口需要调用大模型，响应时间较长
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { data } = response

    // 根据后端返回格式进行适配
    if (data.code === 200 || data.success) {
      return data.data || data
    }

    return data
  },
  (error) => {
    const toastStore = useToastStore()

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          toastStore.showError('登录已过期，请重新登录')
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          toastStore.showError('没有权限访问该资源')
          break
        case 404:
          toastStore.showError('请求的资源不存在')
          break
        case 500:
          toastStore.showError('服务器错误，请稍后重试')
          break
        default:
          toastStore.showError(data?.message || '请求失败，请稍后重试')
      }
    } else if (error.request) {
      toastStore.showError('网络连接失败，请检查网络')
    } else {
      toastStore.showError('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default request
