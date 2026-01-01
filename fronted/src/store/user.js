import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref({
    id: 1,
    username: '学习者',
    avatar: '',
    email: 'learner@example.com'
  })

  const theme = ref(localStorage.getItem('theme') || 'light')

  /**
   * 设置用户信息
   */
  function setUserInfo(info) {
    userInfo.value = { ...userInfo.value, ...info }
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
  }

  /**
   * 切换主题
   */
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    applyTheme()
  }

  /**
   * 设置主题
   */
  function setTheme(newTheme) {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  /**
   * 应用主题
   */
  function applyTheme() {
    if (theme.value === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  /**
   * 退出登录
   */
  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    userInfo.value = null
  }

  // 初始化时应用主题
  applyTheme()

  // 从localStorage恢复用户信息
  const savedUserInfo = localStorage.getItem('userInfo')
  if (savedUserInfo) {
    try {
      userInfo.value = JSON.parse(savedUserInfo)
    } catch (e) {
      console.error('Failed to parse user info:', e)
    }
  }

  return {
    userInfo,
    theme,
    setUserInfo,
    toggleTheme,
    setTheme,
    logout
  }
})
