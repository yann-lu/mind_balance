<template>
  <div class="min-h-screen bg-bg dark:bg-bg-dark">
    <TopBar
      @toggle-sidebar="toggleSidebar"
      @pause-timer="handlePauseTimer"
      @resume-timer="handleResumeTimer"
      @stop-timer="handleStopTimer"
    />

    <Sidebar
      :is-open="sidebarOpen"
      :is-mobile="isMobile"
      @close="closeSidebar"
    />

    <!-- 主内容区 -->
    <main
      class="pt-16 lg:pl-64 transition-all duration-300"
      :class="{ 'pt-32': timerStore.currentTask && isMobile }"
    >
      <div class="p-4 lg:p-6 min-h-[calc(100vh-4rem)]">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>

      <!-- 移动端底部版权 -->
      <div class="lg:hidden p-4 text-center border-t border-gray-200 dark:border-gray-700">
        <p class="text-xs text-gray-400 dark:text-gray-500">学迹 © 2025</p>
      </div>
    </main>

    <!-- Toast 提示 -->
    <TransitionGroup
      name="slide-fade"
      tag="div"
      class="fixed top-20 right-4 z-50 flex flex-col gap-2 pointer-events-none"
    >
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg max-w-sm"
        :class="getToastClass(toast.type)"
      >
        <i :class="getToastIcon(toast.type)" class="text-lg"></i>
        <span class="flex-1 text-sm font-medium">{{ toast.message }}</span>
        <button
          @click="toastStore.removeToast(toast.id)"
          class="p-1 hover:opacity-70"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { TopBar, Sidebar } from './index'
import { useToastStore } from '@/store/toast'
import { useTimerStore } from '@/store/timer'
import { taskApi } from '@/utils/api'
import { formatDuration } from '@/utils/format'

const toastStore = useToastStore()
const timerStore = useTimerStore()

// 侧边栏状态
const sidebarOpen = ref(false)
const isMobile = ref(false)

// 检测屏幕尺寸
function checkScreenSize() {
  isMobile.value = window.innerWidth < 1024
  if (!isMobile.value) {
    sidebarOpen.value = true
  }
}

// 切换侧边栏
function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

// 关闭侧边栏
function closeSidebar() {
  sidebarOpen.value = false
}

// 处理暂停计时
async function handlePauseTimer() {
  timerStore.pauseTimer()
  toastStore.showWarning('计时已暂停')

  // 调用API暂停
  try {
    if (timerStore.currentTask) {
      await taskApi.pauseTimer(timerStore.currentTask.id)
    }
  } catch (error) {
    console.error('Failed to pause timer:', error)
  }
}

// 处理恢复计时
async function handleResumeTimer() {
  timerStore.resumeTimer()
  toastStore.showSuccess('计时继续')

  // 调用API开始
  try {
    if (timerStore.currentTask) {
      await taskApi.startTimer(timerStore.currentTask.id)
    }
  } catch (error) {
    console.error('Failed to resume timer:', error)
  }
}

// 处理停止计时
async function handleStopTimer() {
  const { task, time } = timerStore.stopTimer()

  if (time > 0) {
    toastStore.showSuccess(`本次学习 ${formatDuration(time)}`)
  }

  // 调用API结束
  try {
    if (task) {
      await taskApi.stopTimer(task.id)
    }
  } catch (error) {
    console.error('Failed to stop timer:', error)
  }
}

// 获取Toast样式类
function getToastClass(type) {
  const classes = {
    success: 'bg-white dark:bg-gray-800 border-l-4 border-success text-gray-800 dark:text-gray-200',
    error: 'bg-white dark:bg-gray-800 border-l-4 border-danger text-gray-800 dark:text-gray-200',
    warning: 'bg-white dark:bg-gray-800 border-l-4 border-warning text-gray-800 dark:text-gray-200',
    info: 'bg-white dark:bg-gray-800 border-l-4 border-primary text-gray-800 dark:text-gray-200'
  }
  return classes[type] || classes.info
}

// 获取Toast图标
function getToastIcon(type) {
  const icons = {
    success: 'fas fa-check-circle text-success',
    error: 'fas fa-exclamation-circle text-danger',
    warning: 'fas fa-exclamation-triangle text-warning',
    info: 'fas fa-info-circle text-primary'
  }
  return icons[type] || icons.info
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  timerStore.restoreTimerState()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})
</script>

<style scoped>
/* 确保顶部导航栏高度一致 */
main {
  padding-top: 4rem;
}

@media (min-width: 1024px) {
  main {
    padding-left: 16rem;
  }
}
</style>
