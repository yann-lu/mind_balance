<template>
  <div class="max-w-4xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-4">AI规划接口调试</h1>

    <div class="space-y-4">
      <button
        @click="testGeneratePlan"
        :disabled="loading"
        class="px-6 py-2 bg-primary text-white rounded-lg disabled:opacity-50"
      >
        {{ loading ? '测试中...' : '测试生成计划接口' }}
      </button>

      <div v-if="result" class="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <h3 class="font-semibold mb-2">测试结果</h3>
        <pre class="text-xs overflow-auto">{{ JSON.stringify(result, null, 2) }}</pre>
      </div>

      <div v-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
        <h3 class="font-semibold mb-2 text-red-600">错误信息</h3>
        <pre class="text-xs overflow-auto text-red-700">{{ error }}</pre>
      </div>

      <div v-if="step" class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <h3 class="font-semibold mb-2 text-blue-600">执行步骤</h3>
        <ul class="text-sm space-y-1">
          <li v-for="(s, idx) in steps" :key="idx" class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full" :class="s.done ? 'bg-green-500' : 'bg-gray-400'"></span>
            <span>{{ s.text }}</span>
            <span v-if="s.time" class="text-gray-500">({{ s.time }}ms)</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { aiApi, taskApi, projectApi } from '@/utils/api'

const loading = ref(false)
const result = ref(null)
const error = ref(null)
const steps = ref([])

function addStep(text, time = null) {
  steps.value.push({ text, time, done: !!time })
}

async function testGeneratePlan() {
  loading.value = true
  result.value = null
  error.value = null
  steps.value = []

  const startTime = Date.now()

  try {
    addStep('开始测试生成计划接口')
    const step1Start = Date.now()

    // 步骤1: 调用生成计划接口
    const planData = await aiApi.generatePlan({ period: 'today' })
    const step1Time = Date.now() - step1Start
    addStep(`✓ 生成计划接口返回 (耗时: ${step1Time}ms)`, step1Time)

    console.log('生成计划返回数据:', planData)

    if (!planData.recommendations || planData.recommendations.length === 0) {
      result.value = planData
      return
    }

    // 步骤2: 获取任务详情
    addStep('开始获取任务详情...')
    const step2Start = Date.now()

    const recommendationsWithDetails = await Promise.all(
      planData.recommendations.map(async (rec) => {
        try {
          console.log('获取任务详情:', rec.id)
          const step2aStart = Date.now()

          const [taskDetail, projectDetail] = await Promise.all([
            taskApi.getTaskDetail(rec.id),
            projectApi.getProjectDetail(rec.projectId)
          ])

          const step2aTime = Date.now() - step2aStart
          console.log(`任务${rec.id}详情获取完成 (${step2aTime}ms)`)

          return {
            ...rec,
            ...taskDetail,
            projectName: projectDetail.name,
            icon: projectDetail.icon,
            color: projectDetail.color_hex
          }
        } catch (err) {
          console.error('获取详情失败:', err)
          return rec
        }
      })
    )

    const step2Time = Date.now() - step2Start
    addStep(`✓ 所有任务详情获取完成 (耗时: ${step2Time}ms)`, step2Time)

    // 步骤3: 获取精力建议的项目详情
    if (planData.energySuggestions) {
      addStep('开始获取精力建议项目详情...')
      const step3Start = Date.now()

      const energySuggestionsWithDetails = await Promise.all(
        planData.energySuggestions.map(async (suggestion) => {
          try {
            const projectDetail = await projectApi.getProjectDetail(suggestion.projectId)
            return {
              ...suggestion,
              name: suggestion.projectName,
              icon: projectDetail.icon,
              color: projectDetail.color_hex
            }
          } catch (err) {
            return suggestion
          }
        })
      )

      const step3Time = Date.now() - step3Start
      addStep(`✓ 精力建议详情获取完成 (耗时: ${step3Time}ms)`, step3Time)

      planData.energySuggestions = energySuggestionsWithDetails
    }

    planData.recommendations = recommendationsWithDetails

    const totalTime = Date.now() - startTime
    addStep(`✓ 全部完成 (总耗时: ${totalTime}ms)`, totalTime)

    result.value = planData
  } catch (err) {
    console.error('测试失败:', err)
    error.value = err.toString() + '\n' + err.stack
  } finally {
    loading.value = false
  }
}
</script>
