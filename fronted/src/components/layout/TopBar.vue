<template>
  <header class="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-card-dark shadow-sm">
    <div class="flex items-center justify-between px-4 lg:px-6 h-16">
      <!-- 左侧：Logo + 移动端汉堡菜单 -->
      <div class="flex items-center gap-4">
        <button
          @click="$emit('toggle-sidebar')"
          class="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <i class="fas fa-bars text-xl text-gray-600 dark:text-gray-300"></i>
        </button>

        <router-link to="/" class="flex items-center gap-2">
          <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <i class="fas fa-graduation-cap text-white text-sm"></i>
          </div>
          <span class="text-xl font-semibold text-text-primary dark:text-text-dark">学迹</span>
        </router-link>
      </div>

      <!-- 中间：计时器显示 (PC端) -->
      <div v-if="timerStore.currentTask" class="hidden md:flex items-center gap-3 px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full" :class="timerStore.isRunning ? 'bg-success animate-pulse' : 'bg-warning'"></span>
          <span class="text-sm text-gray-600 dark:text-gray-300 truncate max-w-[150px]">
            {{ timerStore.currentTask.name }}
          </span>
        </div>
        <span class="text-lg font-mono font-semibold text-primary">{{ timerStore.formattedTime }}</span>
        <button
          v-if="timerStore.isRunning"
          @click="$emit('pause-timer')"
          class="p-1 text-warning hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded"
          title="暂停"
        ><i class="fas fa-pause text-sm"></i></button><button
          v-else
          @click="$emit('resume-timer')"
          class="p-1 text-success hover:bg-green-50 dark:hover:bg-green-900/20 rounded"
          title="继续"
        ><i class="fas fa-play text-sm"></i></button>
        <button
          @click="$emit('stop-timer')"
          class="p-1 text-danger hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
          title="结束"
        >
          <i class="fas fa-stop text-sm"></i>
        </button>
      </div>

      <!-- 右侧：用户信息 + 退出 -->
      <div class="flex items-center gap-3">
        <button
          @click="userStore.toggleTheme()"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          title="切换主题"
        >
          <i
            class="fas text-lg"
            :class="userStore.theme === 'dark' ? 'fa-sun text-yellow-400' : 'fa-moon text-gray-600'"
          ></i>
        </button>

        <div class="hidden sm:flex items-center gap-2">
          <div class="w-8 h-8 bg-primary-light dark:bg-gray-700 rounded-full flex items-center justify-center">
            <i class="fas fa-user text-primary dark:text-gray-300 text-sm"></i>
          </div>
          <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ userStore.userInfo?.username }}</span>
        </div>

        <button
          @click="handleLogout"
          class="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          title="退出登录"
        >
          <i class="fas fa-sign-out-alt text-lg text-danger"></i>
        </button>
      </div>
    </div>

    <!-- 移动端计时器条 -->
    <div
      v-if="timerStore.currentTask"
      class="md:hidden flex items-center justify-between px-4 py-2 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
    >
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full" :class="timerStore.isRunning ? 'bg-success animate-pulse' : 'bg-warning'"></span>
        <span class="text-sm text-gray-600 dark:text-gray-300 truncate max-w-[120px]">
          {{ timerStore.currentTask.name }}
        </span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm font-mono font-semibold text-primary">{{ timerStore.formattedTime }}</span>
        <div class="flex items-center gap-1">
          <button
            v-if="timerStore.isRunning"
            @click="$emit('pause-timer')"
            class="p-1.5 text-warning rounded"
          ><i class="fas fa-pause text-xs"></i></button><button
            v-else
            @click="$emit('resume-timer')"
            class="p-1.5 text-success rounded"
          ><i class="fas fa-play text-xs"></i></button>
          <button
            @click="$emit('stop-timer')"
            class="p-1.5 text-danger rounded"
          >
            <i class="fas fa-stop text-xs"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useUserStore } from '@/store/user'
import { useTimerStore } from '@/store/timer'
import { useToastStore } from '@/store/toast'
import { useRouter } from 'vue-router'

defineEmits(['toggle-sidebar', 'pause-timer', 'resume-timer', 'stop-timer'])

const userStore = useUserStore()
const timerStore = useTimerStore()
const toastStore = useToastStore()
const router = useRouter()

function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    userStore.logout()
    toastStore.showInfo('已退出登录')
    router.push('/login')
  }
}
</script>
