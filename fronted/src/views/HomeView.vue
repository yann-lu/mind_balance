<template>
  <div class="space-y-6">
    <!-- 欢迎卡片 -->
    <section class="card p-6 bg-gradient-to-r from-primary to-primary-hover text-white">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-2xl lg:text-3xl font-bold mb-2">
            {{ greeting }}，{{ userStore.userInfo?.username }} 💪
          </h1>
          <p class="text-white/80">{{ currentDate }} {{ weekday }}</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-white/70">今日已学习</span>
          <span class="text-2xl font-bold">{{ formatDurationShort(todayDuration) }}</span>
        </div>
      </div>
    </section>

    <!-- 数据概览 -->
    <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="stat in overviewStats"
        :key="stat.label"
        class="card p-4 lg:p-5"
      >
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">{{ stat.label }}</p>
            <p class="text-2xl lg:text-3xl font-bold text-text-primary dark:text-text-dark">
              {{ stat.value }}
            </p>
          </div>
          <div
            class="w-10 h-10 lg:w-12 lg:h-12 rounded-lg flex items-center justify-center"
            :style="{ backgroundColor: stat.color + '20', color: stat.color }"
          >
            <i :class="stat.icon" class="text-lg lg:text-xl"></i>
          </div>
        </div>
        <div v-if="stat.trend" class="mt-3 flex items-center gap-1 text-xs" :class="stat.trendUp ? 'text-success' : 'text-danger'">
          <i :class="stat.trendUp ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
          <span>{{ stat.trend }}</span>
        </div>
      </div>
    </section>

    <!-- 快捷操作 -->
    <section>
      <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">快捷操作</h2>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <button
          @click="$router.push('/projects?action=new')"
          class="card p-5 text-left group hover:border-primary border-2 border-transparent transition-all"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-primary-light dark:bg-primary/20 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
              <i class="fas fa-plus text-primary text-xl"></i>
            </div>
            <div>
              <h3 class="font-semibold text-text-primary dark:text-text-dark">新建项目</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">创建新的学习项目</p>
            </div>
          </div>
        </button>

        <button
          @click="$router.push('/tasks?action=new')"
          class="card p-5 text-left group hover:border-primary border-2 border-transparent transition-all"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-success/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
              <i class="fas fa-tasks text-success text-xl"></i>
            </div>
            <div>
              <h3 class="font-semibold text-text-primary dark:text-text-dark">新建任务</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">添加新的学习任务</p>
            </div>
          </div>
        </button>

        <button
          @click="startQuickTimer"
          class="card p-5 text-left group hover:border-primary border-2 border-transparent transition-all"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-warning/10 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
              <i class="fas fa-play text-warning text-xl"></i>
            </div>
            <div>
              <h3 class="font-semibold text-text-primary dark:text-text-dark">开始计时</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">快速开始学习计时</p>
            </div>
          </div>
        </button>
      </div>
    </section>

    <!-- AI提醒 + 今日任务 -->
    <section class="grid lg:grid-cols-2 gap-6">
      <!-- AI今日提醒 -->
      <div class="card p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark">
            <i class="fas fa-robot text-primary mr-2"></i>AI提醒
          </h2>
        </div>

        <div v-if="aiReminders.length > 0" class="space-y-3">
          <div
            v-for="reminder in aiReminders"
            :key="reminder.id"
            class="flex items-start gap-3 p-3 rounded-lg"
            :class="reminder.type === 'warning' ? 'bg-red-50 dark:bg-red-900/20' : 'bg-green-50 dark:bg-green-900/20'"
          >
            <i
              :class="reminder.type === 'warning' ? 'fas fa-exclamation-triangle text-warning' : 'fas fa-check-circle text-success'"
              class="mt-0.5"
            ></i>
            <div>
              <p class="text-sm font-medium text-text-primary dark:text-text-dark">{{ reminder.message }}</p>
              <p v-if="reminder.suggestion" class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ reminder.suggestion }}</p>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-400">
          <i class="fas fa-check-circle text-4xl mb-3 text-success/50"></i>
          <p class="text-sm">暂无提醒，状态良好！</p>
        </div>
      </div>

      <!-- 今日任务列表 -->
      <div class="card p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark">
            <i class="fas fa-calendar-day text-primary mr-2"></i>今日任务
          </h2>
          <router-link to="/tasks" class="text-sm text-primary hover:underline">
            查看全部 <i class="fas fa-arrow-right text-xs"></i>
          </router-link>
        </div>

        <div v-if="todayTasks.length > 0" class="space-y-3">
          <div
            v-for="task in todayTasks"
            :key="task.id"
            class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg group hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
            @click="startTask(task)"
          >
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <div
                class="w-2 h-2 rounded-full flex-shrink-0"
                :class="{
                  'bg-gray-300': task.status === 'pending',
                  'bg-primary': task.status === 'in_progress',
                  'bg-success': task.status === 'completed'
                }"
              ></div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-text-primary dark:text-text-dark truncate">{{ task.name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ task.projectName }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span v-if="task.duration" class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatDurationShort(task.duration) }}
              </span>
              <button
                class="opacity-0 group-hover:opacity-100 p-1.5 text-primary hover:bg-primary-light dark:hover:bg-primary/20 rounded-lg transition-all"
                title="开始此任务"
              >
                <i class="fas fa-play text-xs"></i>
              </button>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-400">
          <i class="fas fa-clipboard-list text-4xl mb-3"></i>
          <p class="text-sm">今日暂无任务</p>
          <button
            @click="$router.push('/tasks?action=new')"
            class="mt-3 text-sm text-primary hover:underline"
          >
            添加新任务
          </button>
        </div>
      </div>
    </section>

    <!-- 最近项目 -->
    <section v-if="recentProjects.length > 0">
      <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">最近项目</h2>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="project in recentProjects"
          :key="project.id"
          class="card p-4 cursor-pointer group"
          @click="$router.push(`/projects/${project.id}`)"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-lg flex items-center justify-center"
                :style="{ backgroundColor: project.color + '20' }"
              >
                <i :class="project.icon" class="text-lg" :style="{ color: project.color }"></i>
              </div>
              <div>
                <h3 class="font-semibold text-text-primary dark:text-text-dark group-hover:text-primary transition-colors">
                  {{ project.name }}
                </h3>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ project.taskCount }} 个任务</p>
              </div>
            </div>
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="text-gray-500 dark:text-gray-400">精力占比</span>
              <span class="font-medium" :style="{ color: project.color }">{{ project.energyPercent }}%</span>
            </div>
            <div class="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-300"
                :style="{ width: project.energyPercent + '%', backgroundColor: project.color }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useTimerStore } from '@/store/timer'
import { useToastStore } from '@/store/toast'
import { statisticsApi, aiApi, taskApi, projectApi } from '@/utils/api'
import { getGreeting, formatDate, getWeekday, formatDurationShort, formatDuration } from '@/utils/format'

const router = useRouter()
const userStore = useUserStore()
const timerStore = useTimerStore()
const toastStore = useToastStore()

// 数据状态
const overviewData = ref(null)
const todayDuration = ref(0)
const aiReminders = ref([])
const todayTasks = ref([])
const recentProjects = ref([])

// 计算属性
const greeting = computed(() => getGreeting())

const currentDate = computed(() => {
  return formatDate(new Date(), 'yyyy年MM月dd日')
})

const weekday = computed(() => {
  return getWeekday(new Date())
})

const overviewStats = computed(() => {
  if (!overviewData.value) return []

  return [
    {
      label: '活跃项目',
      value: overviewData.value.activeProjects || 0,
      icon: 'fas fa-folder',
      color: '#4A90E2',
      trend: overviewData.value.projectsTrend,
      trendUp: overviewData.value.projectsTrendUp
    },
    {
      label: '待完成任务',
      value: overviewData.value.pendingTasks || 0,
      icon: 'fas fa-tasks',
      color: '#FF9800',
      trend: overviewData.value.tasksTrend,
      trendUp: false // 任务越少越好
    },
    {
      label: '今日学习',
      value: formatDurationShort(todayDuration.value),
      icon: 'fas fa-clock',
      color: '#66BB6A'
    },
    {
      label: '精力达标率',
      value: (overviewData.value.energyRate || 0) + '%',
      icon: 'fas fa-battery-three-quarters',
      color: '#9C27B0',
      trend: overviewData.value.energyTrend,
      trendUp: true
    }
  ]
})

// 获取概览数据
async function fetchOverviewData() {
  try {
    const data = await statisticsApi.getOverview()
    overviewData.value = data
    todayDuration.value = data.todayDuration || 0
  } catch (error) {
    console.error('Failed to fetch overview:', error)
    overviewData.value = {
      activeProjects: 0,
      pendingTasks: 0,
      energyRate: 0,
      todayDuration: 0
    }
    todayDuration.value = 0
  }
}

// 获取AI提醒
async function fetchAiReminders() {
  try {
    const data = await aiApi.getEnergyWarnings()
    // 转换数据格式以匹配前端
    if (data && Array.isArray(data)) {
      aiReminders.value = data.map(w => ({
        id: w.id || Math.random(),
        type: w.type || 'info',
        message: w.message || w.warning || '',
        suggestion: w.suggestion || ''
      }))
    } else {
      aiReminders.value = []
    }
  } catch (error) {
    console.error('Failed to fetch AI reminders:', error)
    aiReminders.value = []
  }
}

// 获取今日任务
async function fetchTodayTasks() {
  try {
    // 获取所有进行中或未开始的任务
    const data = await taskApi.getTaskList()
    if (data && data.length > 0) {
      // 取前5个任务
      todayTasks.value = data.slice(0, 5).map(t => ({
        id: t.id,
        name: t.title,
        projectName: t.project_name || '未知项目',
        status: t.status === 'todo' ? 'pending' : t.status === 'done' ? 'completed' : t.status,
        duration: t.total_duration || 0
      }))
    } else {
      todayTasks.value = []
    }
  } catch (error) {
    console.error('Failed to fetch today tasks:', error)
    todayTasks.value = []
  }
}

// 获取最近项目
async function fetchRecentProjects() {
  try {
    const data = await projectApi.getProjectList()
    if (data && data.length > 0) {
      // 取前6个项目
      recentProjects.value = data.slice(0, 6).map(p => ({
        id: p.id,
        name: p.name,
        icon: p.icon,
        color: p.color_hex,
        energyPercent: p.energy_percent || 0,
        taskCount: p.total_tasks || 0
      }))
    } else {
      recentProjects.value = []
    }
  } catch (error) {
    console.error('Failed to fetch recent projects:', error)
    recentProjects.value = []
  }
}

// 开始任务计时
async function startTask(task) {
  if (timerStore.currentTask?.id === task.id && timerStore.isRunning) {
    toastStore.showInfo('该任务正在计时中')
    return
  }

  try {
    // 调用后端 API 开始计时
    await taskApi.startTimer(task.id)
    timerStore.startTimer(task)
    toastStore.showSuccess(`开始计时：${task.name}`)
  } catch (error) {
    console.error('Failed to start timer:', error)
    toastStore.showError('开始计时失败')
  }
}

// 快速开始计时
function startQuickTimer() {
  if (todayTasks.value.length > 0) {
    const pendingTask = todayTasks.value.find(t => t.status === 'pending') || todayTasks.value[0]
    startTask(pendingTask)
  } else {
    router.push('/tasks?action=new')
  }
}

onMounted(() => {
  fetchOverviewData()
  fetchAiReminders()
  fetchTodayTasks()
  fetchRecentProjects()
})
</script>
