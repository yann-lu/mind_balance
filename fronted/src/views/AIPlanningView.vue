<template>
  <div class="space-y-6">
    <!-- 页面头部 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-text-primary dark:text-text-dark">
          <i class="fas fa-robot text-primary mr-2"></i>AI 规划
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">智能推荐学习任务，优化精力分配</p>
      </div>
      <BaseButton variant="primary" @click="generatePlan">
        <i class="fas fa-magic mr-2"></i>
        重新生成计划
      </BaseButton>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="space-y-6">
      <div class="card p-6">
        <div class="skeleton h-6 w-1/4 rounded mb-4"></div>
        <div class="space-y-3">
          <div v-for="i in 3" :key="i" class="skeleton h-20 w-full rounded"></div>
        </div>
      </div>
    </div>

    <template v-else>
      <!-- 精力预警 -->
      <section v-if="warnings.length > 0">
        <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
          <i class="fas fa-exclamation-triangle text-warning mr-2"></i>精力预警
        </h2>
        <div class="space-y-3">
          <div
            v-for="warning in warnings"
            :key="warning.id"
            class="card p-4 border-l-4 border-warning bg-red-50 dark:bg-red-900/20"
          >
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-exclamation-triangle text-warning"></i>
              </div>
              <div class="flex-1">
                <h3 class="font-semibold text-text-primary dark:text-text-dark mb-1">
                  {{ warning.title }}
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
                  {{ warning.message }}
                </p>
                <div v-if="warning.suggestions && warning.suggestions.length > 0" class="flex flex-wrap gap-2">
                  <button
                    v-for="(suggestion, idx) in warning.suggestions"
                    :key="idx"
                    @click="applySuggestion(suggestion)"
                    class="text-xs px-3 py-1.5 bg-white dark:bg-gray-800 rounded-lg text-primary hover:bg-primary hover:text-white transition-colors"
                  >
                    <i class="fas fa-lightbulb mr-1"></i>{{ suggestion.text }}
                  </button>
                </div>
              </div>
              <span
                class="badge badge-warning"
              >{{ warning.level === 'high' ? '高' : warning.level === 'medium' ? '中' : '低' }}优先</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 今日推荐任务 -->
      <section>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark">
            <i class="fas fa-star text-warning mr-2"></i>今日推荐任务
          </h2>
          <span class="text-sm text-gray-500 dark:text-gray-400">
            基于你的学习计划和进度智能推荐
          </span>
        </div>

        <div v-if="recommendations.length > 0" class="grid gap-4">
          <div
            v-for="(task, index) in recommendations"
            :key="task.id"
            class="card p-5 relative group hover:border-primary/30 border-2 border-transparent transition-all"
          >
            <!-- 推荐角标 -->
            <div class="absolute -top-2 -left-2 w-8 h-8 bg-gradient-to-br from-warning to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg">
              {{ index + 1 }}
            </div>

            <div class="flex items-start justify-between gap-4 pl-4">
              <div class="flex items-start gap-4 flex-1">
                <div
                  class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                  :style="{ backgroundColor: task.color + '20' }"
                >
                  <i :class="task.icon" class="text-xl" :style="{ color: task.color }"></i>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <h3 class="font-semibold text-text-primary dark:text-text-dark">
                      {{ task.name }}
                    </h3>
                    <span
                      class="badge"
                      :class="{
                        'badge-danger': task.priority === 'high',
                        'badge-warning': task.priority === 'medium',
                        'badge-success': task.priority === 'low'
                      }"
                    >
                      {{ task.priority === 'high' ? '高优先' : task.priority === 'medium' ? '中优先' : '低优先' }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <i class="fas fa-folder mr-1"></i>{{ task.projectName }}
                  </p>
                  <p class="text-sm text-gray-600 dark:text-gray-300">
                    {{ task.reason }}
                  </p>
                </div>
              </div>

              <div class="flex flex-col items-end gap-2">
                <div class="text-right">
                  <p class="text-xs text-gray-500 dark:text-gray-400">预计耗时</p>
                  <p class="text-lg font-semibold text-primary">{{ task.estimatedTime }}</p>
                </div>
                <BaseButton
                  size="sm"
                  variant="primary"
                  @click="startTask(task)"
                >
                  <i class="fas fa-play mr-1"></i>开始
                </BaseButton>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="card p-12 text-center">
          <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <i class="fas fa-check-circle text-4xl text-success"></i>
          </div>
          <h3 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-2">
            太棒了！
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            你已完成所有推荐任务，或者今天没有待办任务
          </p>
        </div>
      </section>

      <!-- 精力分配建议 -->
      <section class="card p-6">
        <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
          <i class="fas fa-chart-pie text-primary mr-2"></i>精力分配建议
        </h2>

        <div class="grid sm:grid-cols-2 gap-4">
          <div
            v-for="item in energySuggestions"
            :key="item.projectId"
            class="p-4 rounded-xl border-2 transition-all"
            :class="item.status === 'balanced'
              ? 'border-success bg-green-50 dark:bg-green-900/20'
              : 'border-warning bg-orange-50 dark:bg-orange-900/20'"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-lg flex items-center justify-center"
                  :style="{ backgroundColor: item.color + '30' }"
                >
                  <i :class="item.icon" :style="{ color: item.color }"></i>
                </div>
                <div>
                  <h4 class="font-semibold text-text-primary dark:text-text-dark">{{ item.name }}</h4>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    目标 {{ item.target }}% · 实际 {{ item.actual }}%
                  </p>
                </div>
              </div>
              <i
                class="fas text-lg"
                :class="item.status === 'balanced' ? 'fa-check-circle text-success' : 'fa-exclamation-circle text-warning'"
              ></i>
            </div>

            <p class="text-sm text-gray-600 dark:text-gray-300">
              {{ item.suggestion }}
            </p>

            <div class="mt-3">
              <div class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-300"
                  :class="item.status === 'balanced' ? 'bg-success' : 'bg-warning'"
                  :style="{ width: item.actual + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 学习建议 -->
      <section class="card p-6 bg-gradient-to-r from-primary/10 to-primary/5 dark:from-primary/20">
        <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
          <i class="fas fa-lightbulb text-warning mr-2"></i>今日学习建议
        </h2>

        <ul class="space-y-3">
          <li
            v-for="(tip, index) in dailyTips"
            :key="index"
            class="flex items-start gap-3"
          >
            <span class="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0 text-sm font-medium">
              {{ index + 1 }}
            </span>
            <span class="text-sm text-gray-700 dark:text-gray-300">{{ tip }}</span>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { BaseButton } from '@/components/common'
import { aiApi, taskApi } from '@/utils/api'
import { useTimerStore } from '@/store/timer'
import { useToastStore } from '@/store/toast'

const router = useRouter()
const timerStore = useTimerStore()
const toastStore = useToastStore()

// 数据状态
const loading = ref(false)
const warnings = ref([])
const recommendations = ref([])
const energySuggestions = ref([])
const dailyTips = ref([])

// 获取AI规划数据
async function fetchAIPlanning() {
  loading.value = true
  try {
    // 获取精力预警
    const warningsData = await aiApi.getEnergyWarnings()
    warnings.value = warningsData || []

    // 获取推荐任务
    const recommendationsData = await aiApi.getTodayRecommendations()
    recommendations.value = recommendationsData || []

    // 生成学习建议
    generateDailyTips()
  } catch (error) {
    console.error('Failed to fetch AI planning:', error)
    // 使用模拟数据
    useMockData()
  } finally {
    loading.value = false
  }
}

// 使用模拟数据
function useMockData() {
  warnings.value = [
    {
      id: 1,
      title: 'Python项目精力超支',
      message: 'Python学习项目本周已投入45%的精力，超过目标35%较多',
      level: 'high',
      suggestions: [
        { text: '调整今日计划，增加英语任务', action: 'adjust_task' },
        { text: '查看数据统计详情', action: 'view_stats' }
      ]
    },
    {
      id: 2,
      title: '数据结构进度滞后',
      message: '数据结构项目本周仅投入15%精力，低于目标20%',
      level: 'medium',
      suggestions: [
        { text: '添加数据结构任务', action: 'add_task' }
      ]
    }
  ]

  recommendations.value = [
    {
      id: 1,
      name: '阅读英语文章',
      projectId: 2,
      projectName: '英语提升',
      icon: 'fas fa-language',
      color: '#66BB6A',
      priority: 'high',
      estimatedTime: '30分钟',
      reason: '英语项目本周精力不足，建议增加投入'
    },
    {
      id: 2,
      name: '链表算法练习',
      projectId: 3,
      projectName: '数据结构',
      icon: 'fas fa-project-diagram',
      color: '#FF9800',
      priority: 'high',
      estimatedTime: '45分钟',
      reason: '数据结构进度滞后，需要优先完成'
    },
    {
      id: 3,
      name: 'Python函数练习',
      projectId: 1,
      projectName: 'Python学习',
      icon: 'fab fa-python',
      color: '#4A90E2',
      priority: 'medium',
      estimatedTime: '25分钟',
      reason: '巩固函数相关知识'
    },
    {
      id: 4,
      name: '复习单词',
      projectId: 2,
      projectName: '英语提升',
      icon: 'fas fa-spell-check',
      color: '#66BB6A',
      priority: 'low',
      estimatedTime: '15分钟',
      reason: '碎片时间可以复习'
    }
  ]

  energySuggestions.value = [
    {
      projectId: 1,
      name: 'Python学习',
      icon: 'fab fa-python',
      color: '#4A90E2',
      target: 35,
      actual: 45,
      status: 'unbalanced',
      suggestion: '本周Python投入较多，建议适当减少，增加其他项目的学习时间'
    },
    {
      projectId: 2,
      name: '英语提升',
      icon: 'fas fa-language',
      color: '#66BB6A',
      target: 25,
      actual: 30,
      status: 'balanced',
      suggestion: '英语学习进度良好，继续保持！'
    },
    {
      projectId: 3,
      name: '数据结构',
      icon: 'fas fa-project-diagram',
      color: '#FF9800',
      target: 20,
      actual: 15,
      status: 'unbalanced',
      suggestion: '数据结构投入不足，建议今日优先完成相关任务'
    }
  ]

  generateDailyTips()
}

// 生成每日学习建议
function generateDailyTips() {
  const hours = new Date().getHours()

  const tips = [
    '根据你的学习习惯，下午是你的高效时段，建议安排难点内容',
    '本周已完成5天学习，保持这个节奏！',
    '番茄工作法可以有效提高学习效率，试试25分钟专注+5分钟休息'
  ]

  if (hours < 12) {
    tips.unshift('上午适合逻辑思维类任务，比如算法练习')
  } else if (hours < 18) {
    tips.unshift('下午可以安排需要记忆的内容，比如单词背诵')
  } else {
    tips.unshift('晚上适合回顾整理，总结今天的学习内容')
  }

  dailyTips.value = tips
}

// 开始任务
async function startTask(task) {
  if (timerStore.currentTask?.id === task.id && timerStore.isRunning) {
    toastStore.showInfo('该任务正在计时中')
    return
  }

  // 这里假设task已经是完整的任务对象，如果不是需要先获取
  const taskData = {
    id: task.id,
    name: task.name,
    projectName: task.projectName
  }

  timerStore.startTimer(taskData)
  toastStore.showSuccess(`开始计时：${task.name}`)

  try {
    await taskApi.startTimer(task.id)
  } catch (error) {
    console.error('Failed to start timer:', error)
  }
}

// 应用建议
function applySuggestion(suggestion) {
  if (suggestion.action === 'view_stats') {
    router.push('/statistics')
  } else if (suggestion.action === 'add_task') {
    router.push('/tasks?action=new')
  } else if (suggestion.action === 'adjust_task') {
    toastStore.showInfo('已根据建议调整今日计划')
  }
}

// 重新生成计划
async function generatePlan() {
  loading.value = true
  try {
    await aiApi.generatePlan({ period: 'today' })
    toastStore.showSuccess('AI计划已更新')
    await fetchAIPlanning()
  } catch (error) {
    console.error('Failed to generate plan:', error)
    toastStore.showError('生成失败，请重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAIPlanning()
})
</script>
