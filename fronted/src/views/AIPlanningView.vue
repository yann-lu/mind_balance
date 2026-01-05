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
      <div class="flex items-center gap-3">
        <!-- 模式切换开关 -->
        <div class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <span class="text-sm text-gray-600 dark:text-gray-400">快速模式</span>
          <button
            @click="toggleUseAI"
            :disabled="loading"
            class="relative w-12 h-6 rounded-full transition-colors"
            :class="useAI ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-600'"
          >
            <div
              class="absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform"
              :class="useAI ? 'left-7' : 'left-1'"
            ></div>
          </button>
          <span class="text-sm text-gray-600 dark:text-gray-400">AI深度</span>
        </div>

        <BaseButton variant="primary" @click="generatePlan" :disabled="loading">
          <i class="fas fa-magic mr-2"></i>
          {{ loading ? '生成中...' : '重新生成计划' }}
        </BaseButton>
      </div>
    </div>

    <!-- AI模式提示 -->
    <div v-if="useAI && !loading" class="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg flex items-start gap-3">
      <i class="fas fa-info-circle text-blue-500 mt-0.5"></i>
      <div class="text-sm text-blue-700 dark:text-blue-300">
        <strong>AI深度分析模式已启用</strong> - 将使用AI完整分析你的学习数据,预计需要15-25秒。推荐理由会更个性化。
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="space-y-6">
      <!-- 进度提示 -->
      <div v-if="progressMessage" class="card p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-800">
        <div class="flex items-center gap-4">
          <div class="relative">
            <div class="w-12 h-12 border-4 border-blue-200 dark:border-blue-800 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
          <div class="flex-1">
            <h3 class="font-semibold text-text-primary dark:text-text-dark text-lg mb-1">
              AI正在分析你的学习数据...
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ progressMessage }}</p>
          </div>
        </div>
      </div>

      <!-- 骨架屏(如果没有进度消息) -->
      <div v-else class="card p-6">
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
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { BaseButton } from '@/components/common'
import { aiApi, taskApi, projectApi } from '@/utils/api'
import { useTimerStore } from '@/store/timer'
import { useToastStore } from '@/store/toast'

const router = useRouter()
const timerStore = useTimerStore()
const toastStore = useToastStore()

// 模式选择
const useAI = ref(false)  // false=快速模式(规则引擎), true=AI深度分析模式
const useStream = ref(true)  // 是否使用流式输出(优化体验)

// 数据状态
const loading = ref(false)
const progressMessage = ref('')  // 进度提示信息
const warnings = ref([])
const recommendations = ref([])
const energySuggestions = ref([])
const dailyTips = ref([])

// 切换AI模式
function toggleUseAI() {
  useAI.value = !useAI.value
  console.log(`[AI规划] 模式已切换: ${useAI.value ? 'AI深度分析' : '快速模式'}`)
  toastStore.showInfo(
    useAI.value
      ? '已切换到AI深度分析模式,正在重新生成...'
      : '已切换到快速模式,正在重新生成...'
  )
  // 自动重新生成计划
  generatePlan()
}

// 使用SSE流式接收数据
async function fetchAIPlanningStream() {
  console.log('[AI规划-流式] 开始接收流式数据')
  loading.value = true
  progressMessage.value = '正在初始化...'
  const startTime = Date.now()

  // 构建URL参数
  const aiMode = useAI.value ? 'full' : 'false'
  const url = `/api/ai/generate-plan-stream?period=today&use_ai=${aiMode}`

  console.log(`[AI规划-流式] 连接: ${url}`)
  console.log(`[AI规划-流式] useAI.value: ${useAI.value}, aiMode: ${aiMode}`)

  try {
    // 使用fetch获取SSE流
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        console.log('[AI规划-流式] 流式传输完成')
        break
      }

      // 解码数据块
      buffer += decoder.decode(value, { stream: true })

      // 按行分割SSE数据
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''  // 保留未完成的行

      for (const line of lines) {
        if (line.startsWith('event:')) {
          const eventType = line.substring(7).trim()
          console.log(`[AI规划-流式] 事件类型: ${eventType}`)
        } else if (line.startsWith('data:')) {
          const data = JSON.parse(line.substring(6).trim())
          handleSSEEvent(data)
        }
      }
    }

    const totalTime = Date.now() - startTime
    console.log(`[AI规划-流式] 总耗时: ${totalTime}ms`)

  } catch (error) {
    console.error('[AI规划-流式] 错误:', error)
    toastStore.showError('流式接收失败,降级使用普通模式')
    // 降级到普通API
    await fetchAIPlanning()
  } finally {
    loading.value = false
    progressMessage.value = ''
  }
}

// 处理SSE事件
function handleSSEEvent(data) {
  console.log('[AI规划-流式] 处理事件:', data)

  // init事件 - 初始化数据
  if (data.message === '基础数据已加载') {
    const initData = data.data
    if (initData.warnings) warnings.value = initData.warnings
    if (initData.recommendations) recommendations.value = initData.recommendations

    // 处理 energySuggestions - 需要补充项目详情
    if (initData.energySuggestions) {
      Promise.all(
        initData.energySuggestions.map(async (suggestion) => {
          try {
            const projectDetail = await projectApi.getProjectDetail(suggestion.projectId).catch(err => {
              console.warn(`[AI规划-流式] 获取项目${suggestion.projectId}详情失败:`, err)
              return null
            })

            if (projectDetail) {
              return {
                ...suggestion,
                name: suggestion.projectName,
                icon: projectDetail.icon,
                color: projectDetail.color_hex
              }
            } else {
              return {
                ...suggestion,
                name: suggestion.projectName,
                icon: 'fas fa-project',
                color: '#4A90E2'
              }
            }
          } catch (err) {
            console.error('[AI规划-流式] 处理精力建议时出错:', err)
            return {
              ...suggestion,
              name: suggestion.projectName,
              icon: 'fas fa-project',
              color: '#4A90E2'
            }
          }
        })
      ).then(enrichedData => {
        energySuggestions.value = enrichedData
        console.log(`[AI规划-流式] 初始化 - 精力建议已补充项目详情`)
      })
    }

    if (initData.dailyTips) dailyTips.value = initData.dailyTips
    progressMessage.value = '基础数据已加载'
    toastStore.showSuccess('基础数据已加载,等待AI分析...')
  }

  // progress事件 - 更新进度
  else if (data.message && (data.step || data.progress)) {
    progressMessage.value = data.message
    console.log(`[AI规划-流式] 进度: ${data.progress || 0}% - ${data.message}`)
  }

  // update事件 - 更新字段
  else if (data.field && data.data) {
    const fieldMap = {
      'warnings': warnings,
      'recommendations': recommendations,
      'energySuggestions': energySuggestions,
      'dailyTips': dailyTips
    }

    if (fieldMap[data.field]) {
      // 特殊处理 energySuggestions - 需要补充项目详情
      if (data.field === 'energySuggestions') {
        // 异步补充项目详情
        Promise.all(
          data.data.map(async (suggestion) => {
            try {
              const projectDetail = await projectApi.getProjectDetail(suggestion.projectId).catch(err => {
                console.warn(`[AI规划-流式] 获取项目${suggestion.projectId}详情失败:`, err)
                return null
              })

              if (projectDetail) {
                return {
                  ...suggestion,
                  name: suggestion.projectName, // 后端返回的是 projectName，前端需要 name
                  icon: projectDetail.icon,
                  color: projectDetail.color_hex
                }
              } else {
                return {
                  ...suggestion,
                  name: suggestion.projectName,
                  icon: 'fas fa-project', // 默认图标
                  color: '#4A90E2' // 默认颜色
                }
              }
            } catch (err) {
              console.error('[AI规划-流式] 处理精力建议时出错:', err)
              return {
                ...suggestion,
                name: suggestion.projectName,
                icon: 'fas fa-project',
                color: '#4A90E2'
              }
            }
          })
        ).then(enrichedData => {
          energySuggestions.value = enrichedData
          console.log(`[AI规划-流式] 精力建议已更新并补充项目详情`)
        })
      } else {
        // 其他字段直接赋值
        fieldMap[data.field].value = data.data
      }

      console.log(`[AI规划-流式] 字段更新: ${data.field}`)

      // 显示更新提示
      const fieldNames = {
        'warnings': '精力预警',
        'recommendations': '推荐任务',
        'energySuggestions': '精力建议',
        'dailyTips': '学习建议'
      }
      toastStore.showInfo(`${fieldNames[data.field]}已更新`)
    }
  }

  // complete事件 - 完成
  else if (data.mode) {
    progressMessage.value = '完成!'
    toastStore.showSuccess(data.message || 'AI分析完成!')
    console.log(`[AI规划-流式] 完成: ${data.mode}`)
  }

  // error事件 - 错误
  else if (data.message && data.message.includes('失败')) {
    toastStore.showError(data.message)
  }
}

// 获取AI规划数据(非流式)
async function fetchAIPlanning() {
  console.log('[AI规划] 开始获取AI规划数据')
  loading.value = true
  const startTime = Date.now()

  try {
    // 直接调用生成计划接口,传递use_ai参数
    console.log(`[AI规划] 调用生成计划接口, 模式: ${useAI.value ? 'AI深度分析' : '快速模式'}...`)
    const step1Start = Date.now()

    const planData = await aiApi.generatePlan({
      period: 'today',
      use_ai: useAI.value
    })

    const step1Time = Date.now() - step1Start
    console.log(`[AI规划] 生成计划接口返回, 耗时: ${step1Time}ms`)

    // 处理返回数据
    if (planData.warnings) {
      warnings.value = planData.warnings
      console.log(`[AI规划] 预警数量: ${planData.warnings.length}`)
    }

    if (planData.recommendations && planData.recommendations.length > 0) {
      console.log(`[AI规划] 开始获取 ${planData.recommendations.length} 个推荐任务的详情...`)
      const step2Start = Date.now()

      // 需要从任务ID获取完整的任务信息
      recommendations.value = await Promise.all(
        planData.recommendations.map(async (rec, index) => {
          try {
            const itemStart = Date.now()
            console.log(`[AI规划] 获取任务${index + 1}/${planData.recommendations.length}详情: ${rec.id}`)

            // 并行获取任务详情和项目详情,提高效率
            const [taskDetail, projectDetail] = await Promise.all([
              taskApi.getTaskDetail(rec.id).catch(err => {
                console.warn(`[AI规划] 获取任务${rec.id}详情失败:`, err)
                return null
              }),
              projectApi.getProjectDetail(rec.projectId).catch(err => {
                console.warn(`[AI规划] 获取项目${rec.projectId}详情失败:`, err)
                return null
              })
            ])

            const itemTime = Date.now() - itemStart
            console.log(`[AI规划] 任务${index + 1}详情获取完成, 耗时: ${itemTime}ms`)

            // 如果获取详情失败,返回原始推荐数据,否则返回合并后的数据
            if (taskDetail && projectDetail) {
              return {
                ...rec,
                ...taskDetail,
                projectName: projectDetail.name,
                icon: projectDetail.icon,
                color: projectDetail.color_hex
              }
            } else {
              console.warn(`[AI规划] 任务${rec.id}详情不完整,使用原始数据`)
              return rec
            }
          } catch (err) {
            console.error(`[AI规划] 处理任务${rec.id}时出错:`, err)
            return rec
          }
        })
      )

      const step2Time = Date.now() - step2Start
      console.log(`[AI规划] 所有推荐任务详情获取完成, 总耗时: ${step2Time}ms`)
    } else {
      recommendations.value = []
      console.log('[AI规划] 没有推荐任务')
    }

    if (planData.energySuggestions && planData.energySuggestions.length > 0) {
      console.log(`[AI规划] 开始获取 ${planData.energySuggestions.length} 个精力建议的项目详情...`)
      const step3Start = Date.now()

      energySuggestions.value = await Promise.all(
        planData.energySuggestions.map(async (suggestion, index) => {
          try {
            const projectDetail = await projectApi.getProjectDetail(suggestion.projectId).catch(err => {
              console.warn(`[AI规划] 获取精力建议项目${suggestion.projectId}详情失败:`, err)
              return null
            })

            if (projectDetail) {
              return {
                ...suggestion,
                name: suggestion.projectName,
                icon: projectDetail.icon,
                color: projectDetail.color_hex
              }
            } else {
              return suggestion
            }
          } catch (err) {
            console.error('[AI规划] 处理精力建议时出错:', err)
            return suggestion
          }
        })
      )

      const step3Time = Date.now() - step3Start
      console.log(`[AI规划] 精力建议详情获取完成, 耗时: ${step3Time}ms`)
    } else {
      energySuggestions.value = []
    }

    // 生成学习建议
    if (planData.dailyTips) {
      dailyTips.value = planData.dailyTips
    } else {
      generateDailyTips()
    }

    const totalTime = Date.now() - startTime
    console.log(`[AI规划] ✓ 所有数据获取完成, 总耗时: ${totalTime}ms`)

  } catch (error) {
    console.error('[AI规划] ✗ 获取AI规划数据失败:', error)
    console.error('[AI规划] 错误堆栈:', error.stack)
    toastStore.showError('获取AI规划数据失败，请先配置AI服务')
    // 使用模拟数据作为后备
    useMockData()
  } finally {
    loading.value = false
    console.log('[AI规划] loading状态已设置为false')
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
// 重新生成计划
async function generatePlan() {
  // 使用流式模式获取更好的体验
  if (useStream.value) {
    await fetchAIPlanningStream()
  } else {
    // 降级到普通模式
    loading.value = true
    try {
      await aiApi.generatePlan({
        period: 'today',
        use_ai: useAI.value
      })
      toastStore.showSuccess(
        useAI.value
          ? 'AI深度分析完成!推荐理由已个性化优化'
          : '计划已快速生成'
      )
      await fetchAIPlanning()
    } catch (error) {
      console.error('Failed to generate plan:', error)
      toastStore.showError('生成失败，请重试')
    } finally {
      loading.value = false
    }
  }
}

onMounted(() => {
  // 初始加载使用流式模式
  if (useStream.value) {
    fetchAIPlanningStream()
  } else {
    fetchAIPlanning()
  }
})
</script>
