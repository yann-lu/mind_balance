import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTimerStore = defineStore('timer', () => {
  // 当前计时状态
  const currentTask = ref(null)
  const isRunning = ref(false)
  const elapsedSeconds = ref(0)
  const startTime = ref(null)
  const timerInterval = ref(null)

  // 计算属性：格式化后的时长
  const formattedTime = computed(() => {
    const hours = Math.floor(elapsedSeconds.value / 3600)
    const minutes = Math.floor((elapsedSeconds.value % 3600) / 60)
    const seconds = elapsedSeconds.value % 60

    return [hours, minutes, seconds]
      .map(v => v.toString().padStart(2, '0'))
      .join(':')
  })

  /**
   * 开始计时
   * @param {object} task - 任务对象
   */
  function startTimer(task) {
    if (isRunning.value && currentTask.value?.id === task.id) {
      return // 已经在计时同一个任务
    }

    // 如果有正在计时的任务，先停止
    if (isRunning.value) {
      stopTimer()
    }

    currentTask.value = task
    isRunning.value = true
    startTime.value = Date.now()
    elapsedSeconds.value = 0

    // 启动定时器
    timerInterval.value = setInterval(() => {
      elapsedSeconds.value = Math.floor((Date.now() - startTime.value) / 1000)
    }, 1000)

    // 保存到localStorage
    saveTimerState()
  }

  /**
   * 暂停计时
   */
  function pauseTimer() {
    if (!isRunning.value) return

    if (timerInterval.value) {
      clearInterval(timerInterval.value)
      timerInterval.value = null
    }
    isRunning.value = false
    saveTimerState()
  }

  /**
   * 恢复计时
   */
  function resumeTimer() {
    if (isRunning.value || !currentTask.value) return

    isRunning.value = true
    startTime.value = Date.now() - elapsedSeconds.value * 1000

    timerInterval.value = setInterval(() => {
      elapsedSeconds.value = Math.floor((Date.now() - startTime.value) / 1000)
    }, 1000)

    saveTimerState()
  }

  /**
   * 停止计时
   */
  function stopTimer() {
    const task = currentTask.value
    const time = elapsedSeconds.value

    if (timerInterval.value) {
      clearInterval(timerInterval.value)
      timerInterval.value = null
    }

    currentTask.value = null
    isRunning.value = false
    elapsedSeconds.value = 0
    startTime.value = null

    clearTimerState()

    return { task, time }
  }

  /**
   * 保存计时状态到localStorage
   */
  function saveTimerState() {
    const state = {
      currentTask: currentTask.value,
      isRunning: isRunning.value,
      elapsedSeconds: elapsedSeconds.value,
      startTime: startTime.value
    }
    localStorage.setItem('timerState', JSON.stringify(state))
  }

  /**
   * 从localStorage恢复计时状态
   */
  function restoreTimerState() {
    const saved = localStorage.getItem('timerState')
    if (saved) {
      try {
        const state = JSON.parse(saved)
        if (state.currentTask && state.isRunning) {
          currentTask.value = state.currentTask
          elapsedSeconds.value = state.elapsedSeconds || 0
          // 恢复时自动暂停，避免时间跳跃
          isRunning.value = false
          saveTimerState()
        }
      } catch (e) {
        console.error('Failed to restore timer state:', e)
      }
    }
  }

  /**
   * 清除计时状态
   */
  function clearTimerState() {
    localStorage.removeItem('timerState')
  }

  /**
   * 重置计时器
   */
  function resetTimer() {
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
      timerInterval.value = null
    }
    currentTask.value = null
    isRunning.value = false
    elapsedSeconds.value = 0
    startTime.value = null
    clearTimerState()
  }

  return {
    currentTask,
    isRunning,
    elapsedSeconds,
    formattedTime,
    startTimer,
    pauseTimer,
    resumeTimer,
    stopTimer,
    resetTimer,
    restoreTimerState
  }
})
