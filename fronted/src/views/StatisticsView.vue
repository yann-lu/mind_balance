<template>
  <div class="space-y-6">
    <!-- 页面头部 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-text-primary dark:text-text-dark">数据统计</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">可视化展示你的学习数据</p>
      </div>

      <!-- 时间筛选 -->
      <div class="flex items-center gap-2">
        <button
          v-for="period in periods"
          :key="period.value"
          @click="selectedPeriod = period.value"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
          :class="selectedPeriod === period.value
            ? 'bg-primary text-white'
            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="grid sm:grid-cols-2 gap-6">
      <div v-for="i in 3" :key="i" class="card p-6">
        <div class="skeleton h-6 w-1/3 rounded mb-4"></div>
        <div class="skeleton h-48 w-full rounded"></div>
      </div>
    </div>

    <template v-else>
      <!-- 概览卡片 -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="card p-4">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">总学习时长</p>
          <p class="text-2xl font-bold text-text-primary dark:text-text-dark">
            {{ formatDurationShort(overviewData.totalDuration || 0) }}
          </p>
        </div>
        <div class="card p-4">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">完成任务数</p>
          <p class="text-2xl font-bold text-text-primary dark:text-text-dark">
            {{ overviewData.completedTasks || 0 }}
          </p>
        </div>
        <div class="card p-4">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">学习天数</p>
          <p class="text-2xl font-bold text-text-primary dark:text-text-dark">
            {{ overviewData.studyDays || 0 }}
          </p>
        </div>
        <div class="card p-4">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">日均时长</p>
          <p class="text-2xl font-bold text-text-primary dark:text-text-dark">
            {{ formatDurationShort(overviewData.avgDailyDuration || 0) }}
          </p>
        </div>
      </section>

      <!-- 图表区域 -->
      <div class="grid lg:grid-cols-2 gap-6">
        <!-- 项目时间占比（环形图） -->
        <div class="card p-6">
          <h3 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
            <i class="fas fa-chart-pie text-primary mr-2"></i>项目时间占比
          </h3>
          <div class="relative h-64">
            <Doughnut
              v-if="projectTimeData.labels.length > 0"
              :data="projectTimeData"
              :options="chartOptions.doughnut"
            />
            <div v-else class="absolute inset-0 flex items-center justify-center text-gray-400">
              <div class="text-center">
                <i class="fas fa-chart-pie text-4xl mb-3"></i>
                <p class="text-sm">暂无数据</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 精力分配对比（柱状图） -->
        <div class="card p-6">
          <h3 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
            <i class="fas fa-chart-bar text-primary mr-2"></i>精力分配对比
          </h3>
          <div class="relative h-64">
            <Bar
              v-if="energyData.labels.length > 0"
              :data="energyData"
              :options="chartOptions.bar"
            />
            <div v-else class="absolute inset-0 flex items-center justify-center text-gray-400">
              <div class="text-center">
                <i class="fas fa-chart-bar text-4xl mb-3"></i>
                <p class="text-sm">暂无数据</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 项目详细数据 -->
      <section class="card p-6">
        <h3 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
          <i class="fas fa-list text-primary mr-2"></i>项目详细数据
        </h3>

        <div v-if="projectDetails.length > 0" class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700">
                <th class="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">项目</th>
                <th class="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">总时长</th>
                <th class="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">任务数</th>
                <th class="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">目标精力</th>
                <th class="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">实际精力</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="project in projectDetails"
                :key="project.id"
                class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <td class="py-3 px-4">
                  <div class="flex items-center gap-3">
                    <div
                      class="w-8 h-8 rounded-lg flex items-center justify-center"
                      :style="{ backgroundColor: project.color + '20' }"
                    >
                      <i :class="project.icon" class="text-sm" :style="{ color: project.color }"></i>
                    </div>
                    <span class="font-medium text-text-primary dark:text-text-dark">{{ project.name }}</span>
                  </div>
                </td>
                <td class="text-right py-3 px-4 text-sm text-gray-600 dark:text-gray-300">
                  {{ formatDurationShort(project.totalDuration) }}
                </td>
                <td class="text-right py-3 px-4 text-sm text-gray-600 dark:text-gray-300">
                  {{ project.completedTasks }}/{{ project.totalTasks }}
                </td>
                <td class="text-right py-3 px-4">
                  <span class="text-sm font-medium" :style="{ color: project.color }">
                    {{ project.targetEnergy }}%
                  </span>
                </td>
                <td class="text-right py-3 px-4">
                  <span
                    class="text-sm font-medium"
                    :class="Math.abs(project.actualEnergy - project.targetEnergy) > 10 ? 'text-warning' : 'text-success'"
                  >
                    {{ project.actualEnergy }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="text-center py-12 text-gray-400">
          <i class="fas fa-folder-open text-4xl mb-3"></i>
          <p class="text-sm">暂无项目数据</p>
        </div>
      </section>

      <!-- 每日学习时长趋势（折线图） -->
      <section class="card p-6">
        <h3 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
          <i class="fas fa-chart-line text-primary mr-2"></i>每日学习时长趋势
        </h3>
        <div class="relative h-72">
          <Line
            v-if="dailyTrendData.labels.length > 0"
            :data="dailyTrendData"
            :options="chartOptions.line"
          />
          <div v-else class="absolute inset-0 flex items-center justify-center text-gray-400">
            <div class="text-center">
              <i class="fas fa-chart-line text-4xl mb-3"></i>
              <p class="text-sm">暂无学习数据，开始记录吧 📝</p>
            </div>
          </div>
        </div>

        <!-- 每日学习明细列表 -->
        <div v-if="dailyTrendData.labels.length > 0" class="mt-6">
          <h4 class="text-md font-semibold text-text-primary dark:text-text-dark mb-3">
            <i class="fas fa-table text-primary mr-2"></i>每日明细
          </h4>
          <div class="overflow-x-auto max-h-64 overflow-y-auto">
            <table class="w-full">
              <thead class="sticky top-0 bg-white dark:bg-gray-800">
                <tr class="border-b border-gray-200 dark:border-gray-700">
                  <th class="text-left py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">日期</th>
                  <th class="text-right py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">学习时长</th>
                  <th class="text-right py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-300">占比</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in dailyTrendList"
                  :key="index"
                  class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  <td class="py-2 px-4 text-sm text-text-primary dark:text-text-dark">
                    {{ item.date }}
                  </td>
                  <td class="text-right py-2 px-4 text-sm text-gray-600 dark:text-gray-300">
                    {{ formatDurationShort(item.duration) }}
                  </td>
                  <td class="text-right py-2 px-4 text-sm">
                    <div class="flex items-center justify-end gap-2">
                      <div class="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          class="h-full bg-primary rounded-full transition-all"
                          :style="{ width: item.percentage + '%' }"
                        ></div>
                      </div>
                      <span class="text-gray-600 dark:text-gray-300">{{ item.percentage }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title
} from 'chart.js'
import { Doughnut, Bar, Line } from 'vue-chartjs'
import { statisticsApi, projectApi } from '@/utils/api'
import { formatDurationShort } from '@/utils/format'

// 注册 Chart.js 组件
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title
)

// 数据状态
const loading = ref(false)
const selectedPeriod = ref('week')

const overviewData = ref({
  totalDuration: 0,
  completedTasks: 0,
  studyDays: 0,
  avgDailyDuration: 0
})

const projectTimeData = ref({
  labels: [],
  datasets: [{
    data: [],
    backgroundColor: [],
    borderWidth: 0
  }]
})

const energyData = ref({
  labels: [],
  datasets: [
    {
      label: '目标精力',
      data: [],
      backgroundColor: 'rgba(74, 144, 226, 0.5)',
      borderRadius: 8
    },
    {
      label: '实际精力',
      data: [],
      backgroundColor: 'rgba(102, 187, 106, 0.5)',
      borderRadius: 8
    }
  ]
})

const dailyTrendData = ref({
  labels: [],
  datasets: [{
    label: '学习时长（分钟）',
    data: [],
    borderColor: '#4A90E2',
    backgroundColor: 'rgba(74, 144, 226, 0.1)',
    fill: true,
    tension: 0.4,
    pointRadius: 4,
    pointHoverRadius: 6
  }]
})

const projectDetails = ref([])

// 计算每日趋势列表（用于明细显示）
const dailyTrendList = computed(() => {
  const totalDuration = dailyTrendData.value.datasets[0].data.reduce((a, b) => a + b, 0)
  return dailyTrendData.value.labels.map((label, index) => {
    const duration = dailyTrendData.value.datasets[0].data[index] * 60 // 转换为秒
    const percentage = totalDuration > 0 ? Math.round((duration / (totalDuration * 60)) * 100) : 0

    // 格式化日期显示
    let displayDate = label
    if (label.match(/^\d{4}-\d{2}-\d{2}$/)) {
      const date = new Date(label)
      const today = new Date()
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)

      if (label === today.toISOString().split('T')[0]) {
        displayDate = '今天'
      } else if (label === yesterday.toISOString().split('T')[0]) {
        displayDate = '昨天'
      } else {
        const month = date.getMonth() + 1
        const day = date.getDate()
        const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        const weekday = weekdays[date.getDay()]
        displayDate = `${month}月${day}日 ${weekday}`
      }
    }

    return {
      date: displayDate,
      duration: duration,
      percentage: percentage
    }
  }).reverse() // 最新的日期显示在前面
})

// 时间周期选项
const periods = [
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '全部', value: 'all' }
]

// 图表配置
const chartOptions = {
  doughnut: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || ''
            const value = context.parsed || 0
            const total = context.dataset.data.reduce((a, b) => a + b, 0)
            const percentage = Math.round((value / total) * 100)
            return `${label}: ${formatDurationShort(value * 60)} (${percentage}%)`
          }
        }
      }
    },
    cutout: '65%'
  },
  bar: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value) => value + '%'
        }
      }
    }
  },
  line: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.parsed.y
            return `学习时长: ${Math.round(value)}分钟`
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => value + 'm'
        }
      }
    }
  }
}

// 获取统计数据
async function fetchStatistics() {
  loading.value = true
  try {
    // 获取概览数据 - 需要传入period参数
    const overview = await statisticsApi.getOverview({ period: selectedPeriod.value })
    overviewData.value = overview || overviewData.value

    // 获取项目时间分布
    const projectTime = await statisticsApi.getProjectTimeDistribution({ period: selectedPeriod.value })
    if (projectTime && projectTime.length > 0) {
      projectTimeData.value = {
        labels: projectTime.map(p => p.name),
        datasets: [{
          data: projectTime.map(p => Math.round(p.duration / 60)), // 转换为分钟
          backgroundColor: projectTime.map(p => p.color_hex || p.color),
          borderWidth: 0
        }]
      }
    }

    // 获取精力分配
    const energy = await statisticsApi.getEnergyDistribution({ period: selectedPeriod.value })
    if (energy && energy.length > 0) {
      energyData.value = {
        labels: energy.map(e => e.name),
        datasets: [
          {
            label: '目标精力',
            data: energy.map(e => e.targetEnergy),
            backgroundColor: 'rgba(74, 144, 226, 0.7)',
            borderRadius: 8
          },
          {
            label: '实际精力',
            data: energy.map(e => e.actualEnergy),
            backgroundColor: 'rgba(102, 187, 106, 0.7)',
            borderRadius: 8
          }
        ]
      }

      // 计算项目详细数据
      projectDetails.value = energy.map(e => ({
        ...e,
        color: e.color_hex || e.color,
        completedTasks: e.completedTasks || 0,
        totalTasks: e.totalTasks || 0,
        totalDuration: e.totalDuration || 0
      }))
    }

    // 获取每日趋势
    const dailyTrend = await statisticsApi.getDailyTrend({ period: selectedPeriod.value })
    if (dailyTrend && dailyTrend.length > 0) {
      dailyTrendData.value = {
        labels: dailyTrend.map(d => d.date),
        datasets: [{
          label: '学习时长（分钟）',
          data: dailyTrend.map(d => Math.round(d.duration / 60)),
          borderColor: '#4A90E2',
          backgroundColor: 'rgba(74, 144, 226, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      }
    }
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
    // 使用模拟数据
    useMockData()
  } finally {
    loading.value = false
  }
}

// 使用模拟数据
function useMockData() {
  const colors = ['#4A90E2', '#66BB6A', '#FF9800', '#9C27B0']

  overviewData.value = {
    totalDuration: 16200, // 4.5小时
    completedTasks: 15,
    studyDays: 7,
    avgDailyDuration: 2314 // 约38分钟/天
  }

  projectTimeData.value = {
    labels: ['Python学习', '英语提升', '数据结构'],
    datasets: [{
      data: [120, 90, 60], // 分钟
      backgroundColor: colors,
      borderWidth: 0
    }]
  }

  energyData.value = {
    labels: ['Python学习', '英语提升', '数据结构'],
    datasets: [
      {
        label: '目标精力',
        data: [35, 25, 20],
        backgroundColor: 'rgba(74, 144, 226, 0.7)',
        borderRadius: 8
      },
      {
        label: '实际精力',
        data: [45, 30, 15],
        backgroundColor: 'rgba(102, 187, 106, 0.7)',
        borderRadius: 8
      }
    ]
  }

  dailyTrendData.value = {
    labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    datasets: [{
      label: '学习时长（分钟）',
      data: [30, 45, 25, 60, 40, 55, 35],
      borderColor: '#4A90E2',
      backgroundColor: 'rgba(74, 144, 226, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6
    }]
  }

  projectDetails.value = [
    {
      id: 1,
      name: 'Python学习',
      icon: 'fab fa-python',
      color: '#4A90E2',
      totalDuration: 7200,
      completedTasks: 8,
      totalTasks: 12,
      targetEnergy: 35,
      actualEnergy: 45
    },
    {
      id: 2,
      name: '英语提升',
      icon: 'fas fa-language',
      color: '#66BB6A',
      totalDuration: 5400,
      completedTasks: 5,
      totalTasks: 8,
      targetEnergy: 25,
      actualEnergy: 30
    },
    {
      id: 3,
      name: '数据结构',
      icon: 'fas fa-project-diagram',
      color: '#FF9800',
      totalDuration: 3600,
      completedTasks: 3,
      totalTasks: 6,
      targetEnergy: 20,
      actualEnergy: 15
    }
  ]
}

// 监听时间周期变化
watch(selectedPeriod, () => {
  fetchStatistics()
})

onMounted(() => {
  fetchStatistics()
})
</script>
