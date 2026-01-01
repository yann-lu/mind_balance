import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])

  /**
   * 显示提示消息
   * @param {string} message - 消息内容
   * @param {string} type - 消息类型: success | error | warning | info
   * @param {number} duration - 持续时间(毫秒)
   */
  function showToast(message, type = 'info', duration = 3000) {
    const id = Date.now()
    const toast = {
      id,
      message,
      type,
      duration
    }
    toasts.value.push(toast)

    // 自动移除
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  /**
   * 显示成功消息
   */
  function showSuccess(message, duration) {
    return showToast(message, 'success', duration)
  }

  /**
   * 显示错误消息
   */
  function showError(message, duration) {
    return showToast(message, 'error', duration)
  }

  /**
   * 显示警告消息
   */
  function showWarning(message, duration) {
    return showToast(message, 'warning', duration)
  }

  /**
   * 显示信息消息
   */
  function showInfo(message, duration) {
    return showToast(message, 'info', duration)
  }

  /**
   * 移除提示消息
   */
  function removeToast(id) {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  /**
   * 清空所有提示
   */
  function clearAll() {
    toasts.value = []
  }

  return {
    toasts,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeToast,
    clearAll
  }
})
