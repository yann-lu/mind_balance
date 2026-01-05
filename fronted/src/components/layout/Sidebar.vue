<template>
  <!-- 移动端遮罩 -->
  <transition name="fade">
    <div
      v-if="isOpen && isMobile"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
      @click="$emit('close')"
    ></div>
  </transition>

  <!-- 侧边栏 -->
  <aside
    class="fixed top-16 left-0 bottom-0 z-40 w-64 bg-white dark:bg-card-dark shadow-lg transform transition-transform duration-300 lg:translate-x-0"
    :class="isOpen || !isMobile ? 'translate-x-0' : '-translate-x-full'"
  >
    <nav class="h-full overflow-y-auto py-4">
      <ul class="space-y-1 px-3">
        <li v-for="item in menuItems" :key="item.path">
          <router-link
            :to="item.path"
            @click="handleMenuClick(item.path)"
            class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200"
            :class="isActive(item.path)
              ? 'bg-primary text-white shadow-md'
              : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
          >
            <i :class="item.icon" class="w-5 text-center"></i>
            <span class="font-medium">{{ item.label }}</span>
            <span
              v-if="item.badge"
              class="ml-auto px-2 py-0.5 text-xs font-bold rounded-full"
              :class="isActive(item.path) ? 'bg-white/20 text-white' : 'bg-danger text-white'"
            >
              {{ item.badge }}
            </span>
          </router-link>
        </li>
      </ul>

      <!-- 底部版权信息 -->
      <div class="absolute bottom-0 left-0 right-0 p-4 text-center border-t border-gray-200 dark:border-gray-700">
        <p class="text-xs text-gray-400 dark:text-gray-500">学迹 © 2025</p>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useTimerStore } from '@/store/timer'

const props = defineProps({
  isOpen: Boolean,
  isMobile: Boolean
})

defineEmits(['close'])

const route = useRoute()
const timerStore = useTimerStore()

// 菜单项配置
const menuItems = computed(() => [
  {
    path: '/',
    label: '首页',
    icon: 'fas fa-home'
  },
  {
    path: '/projects',
    label: '项目管理',
    icon: 'fas fa-folder'
  },
  {
    path: '/tasks',
    label: '任务管理',
    icon: 'fas fa-tasks',
    badge: timerStore.isRunning ? '●' : null
  },
  {
    path: '/statistics',
    label: '数据统计',
    icon: 'fas fa-chart-bar'
  },
  {
    path: '/ai-planning',
    label: 'AI规划',
    icon: 'fas fa-robot'
  },
  {
    path: '/deepseek-test',
    label: 'DeepSeek测试',
    icon: 'fas fa-flask'
  },
  {
    path: '/settings',
    label: '设置',
    icon: 'fas fa-cog'
  }
])

// 判断是否激活
function isActive(path) {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

// 处理菜单点击
function handleMenuClick(path) {
  // 移动端点击后关闭侧边栏
  if (props.isMobile) {
    // emit close 事件由父组件处理
  }
}
</script>
