<template>
  <div class="space-y-6 max-w-3xl">
    <!-- 页面头部 -->
    <div>
      <h1 class="text-2xl font-bold text-text-primary dark:text-text-dark">设置</h1>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">管理你的账户和应用设置</p>
    </div>

    <!-- 个人信息 -->
    <section class="card p-6">
      <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
        <i class="fas fa-user text-primary mr-2"></i>个人信息
      </h2>

      <form @submit.prevent="handleUpdateProfile">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            <i class="fas fa-user text-2xl text-primary"></i>
          </div>
          <div>
            <p class="font-medium text-text-primary dark:text-text-dark">{{ userStore.userInfo?.username }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ userStore.userInfo?.email }}</p>
          </div>
        </div>

        <div class="grid sm:grid-cols-2 gap-4">
          <BaseInput
            v-model="profileForm.username"
            label="用户名"
            placeholder="请输入用户名"
            required
          />

          <BaseInput
            v-model="profileForm.email"
            label="邮箱"
            type="email"
            placeholder="请输入邮箱"
          />
        </div>

        <div class="flex justify-end mt-4">
          <BaseButton variant="primary" type="submit" :loading="profileSubmitting">
            保存修改
          </BaseButton>
        </div>
      </form>
    </section>

    <!-- AI配置 -->
    <section class="card p-6">
      <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
        <i class="fas fa-robot text-primary mr-2"></i>AI 配置
      </h2>

      <div class="mb-6">
        <BaseButton variant="primary" @click="showAddConfigModal = true">
          <i class="fas fa-plus mr-2"></i>添加AI配置
        </BaseButton>
      </div>

      <div v-if="loadingConfigs" class="space-y-3">
        <div v-for="i in 2" :key="i" class="skeleton h-24 w-full rounded-lg"></div>
      </div>

      <div v-else-if="aiConfigs.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <i class="fas fa-robot text-4xl mb-3"></i>
        <p>还没有配置AI服务</p>
        <p class="text-sm">添加DeepSeek、千问等AI服务来启用智能规划功能</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="config in aiConfigs"
          :key="config.id"
          class="p-4 rounded-xl border-2 transition-all"
          :class="config.isActive
            ? 'border-primary bg-primary/5'
            : 'border-gray-200 dark:border-gray-700'"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center"
                :class="config.isActive ? 'bg-primary/20' : 'bg-gray-100 dark:bg-gray-800'">
                <i class="fas fa-robot text-primary"></i>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <p class="font-medium text-text-primary dark:text-text-dark">
                    {{ getProviderDisplayName(config.provider) }}
                  </p>
                  <span v-if="config.isActive" class="badge badge-success text-xs">当前激活</span>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ config.model || '默认模型' }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <BaseButton
                v-if="!config.isActive"
                size="sm"
                variant="ghost"
                @click="activateConfig(config.id)"
              >
                <i class="fas fa-check mr-1"></i>激活
              </BaseButton>
              <BaseButton
                size="sm"
                variant="ghost"
                @click="editConfig(config)"
              >
                <i class="fas fa-edit"></i>
              </BaseButton>
              <BaseButton
                size="sm"
                variant="ghost-danger"
                @click="confirmDeleteConfig(config)"
              >
                <i class="fas fa-trash"></i>
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 主题设置 -->
    <section class="card p-6">
      <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
        <i class="fas fa-palette text-primary mr-2"></i>主题设置
      </h2>

      <div class="grid grid-cols-2 gap-4">
        <button
          @click="setTheme('light')"
          class="p-4 rounded-xl border-2 transition-all flex items-center gap-3"
          :class="userStore.theme === 'light'
            ? 'border-primary bg-primary/5'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'"
        >
          <div class="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
            <i class="fas fa-sun text-warning"></i>
          </div>
          <div class="text-left">
            <p class="font-medium text-text-primary dark:text-text-dark">浅色模式</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">明亮清爽</p>
          </div>
          <i
            v-if="userStore.theme === 'light'"
            class="fas fa-check-circle text-primary ml-auto"
          ></i>
        </button>

        <button
          @click="setTheme('dark')"
          class="p-4 rounded-xl border-2 transition-all flex items-center gap-3"
          :class="userStore.theme === 'dark'
            ? 'border-primary bg-primary/5'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'"
        >
          <div class="w-10 h-10 rounded-lg bg-gray-800 flex items-center justify-center">
            <i class="fas fa-moon text-primary"></i>
          </div>
          <div class="text-left">
            <p class="font-medium text-text-primary dark:text-text-dark">深色模式</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">护眼舒适</p>
          </div>
          <i
            v-if="userStore.theme === 'dark'"
            class="fas fa-check-circle text-primary ml-auto"
          ></i>
        </button>
      </div>
    </section>

    <!-- 数据管理 -->
    <section class="card p-6">
      <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
        <i class="fas fa-database text-primary mr-2"></i>数据管理
      </h2>

      <div class="space-y-4">
        <!-- 导出数据 -->
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
          <div>
            <p class="font-medium text-text-primary dark:text-text-dark">导出数据</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">导出所有学习数据为JSON文件</p>
          </div>
          <BaseButton variant="ghost" @click="exportData" :loading="exporting">
            <i class="fas fa-download mr-2"></i>导出
          </BaseButton>
        </div>

        <!-- 清空缓存 -->
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
          <div>
            <p class="font-medium text-text-primary dark:text-text-dark">清空缓存</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">清除应用缓存数据，不会删除学习记录</p>
          </div>
          <BaseButton variant="ghost" @click="clearCache" :loading="clearing">
            <i class="fas fa-broom mr-2"></i>清空
          </BaseButton>
        </div>

        <!-- 危险区域 -->
        <div class="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-xl">
          <div>
            <p class="font-medium text-danger">删除所有数据</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">永久删除所有学习记录，此操作不可恢复</p>
          </div>
          <BaseButton variant="ghost-danger" @click="confirmDeleteAll">
            <i class="fas fa-trash mr-2"></i>删除
          </BaseButton>
        </div>
      </div>
    </section>

    <!-- 关于 -->
    <section class="card p-6">
      <h2 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-4">
        <i class="fas fa-info-circle text-primary mr-2"></i>关于
      </h2>

      <div class="space-y-3 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">应用名称</span>
          <span class="font-medium text-text-primary dark:text-text-dark">学迹</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">版本</span>
          <span class="font-medium text-text-primary dark:text-text-dark">v1.0.0</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">技术栈</span>
          <span class="font-medium text-text-primary dark:text-text-dark">Vue3 + Vite + Tailwind CSS</span>
        </div>
      </div>
    </section>

    <!-- AI配置添加/编辑弹窗 -->
    <BaseModal
      :isOpen="showAddConfigModal"
      :title="editingConfig ? '编辑AI配置' : '添加AI配置'"
      @close="closeConfigModal"
    >
      <form @submit.prevent="saveAIConfig" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            AI服务商
          </label>
          <select
            v-model="configForm.provider"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-text-primary dark:text-text-dark"
            required
          >
            <option value="">请选择</option>
            <option value="deepseek">DeepSeek</option>
            <option value="qwen">千问 (Qwen)</option>
            <option value="openai">OpenAI</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            API Key <span class="text-red-500">*</span>
          </label>
          <input
            v-model="configForm.apiKey"
            type="password"
            placeholder="请输入API Key"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-text-primary dark:text-text-dark"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            API Endpoint
          </label>
          <input
            v-model="configForm.apiBase"
            type="text"
            placeholder="自定义API端点（可选）"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-text-primary dark:text-text-dark"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            留空使用默认端点
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            模型名称
          </label>
          <input
            v-model="configForm.model"
            type="text"
            placeholder="模型名称（可选）"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-text-primary dark:text-text-dark"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            留空使用默认模型
          </p>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <BaseButton variant="ghost" @click="closeConfigModal">
            取消
          </BaseButton>
          <BaseButton variant="primary" type="submit" :loading="savingConfig">
            保存
          </BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { BaseInput, BaseButton, BaseModal } from '@/components/common'
import { useUserStore } from '@/store/user'
import { useToastStore } from '@/store/toast'
import { userApi, settingsApi } from '@/utils/api'
import axios from 'axios'

const userStore = useUserStore()
const toastStore = useToastStore()

// 表单状态
const profileForm = ref({
  username: '',
  email: ''
})
const profileSubmitting = ref(false)
const exporting = ref(false)
const clearing = ref(false)

// AI配置状态
const aiConfigs = ref([])
const loadingConfigs = ref(false)
const showAddConfigModal = ref(false)
const editingConfig = ref(null)
const savingConfig = ref(false)
const configForm = ref({
  provider: '',
  apiKey: '',
  apiBase: '',
  model: ''
})

// 初始化表单
onMounted(() => {
  profileForm.value = {
    username: userStore.userInfo?.username || '',
    email: userStore.userInfo?.email || ''
  }
  fetchAIConfigs()
})

// 获取AI配置列表
async function fetchAIConfigs() {
  loadingConfigs.value = true
  try {
    const response = await axios.get('/api/ai/configs')
    aiConfigs.value = response.data.map(config => ({
      ...config,
      isActive: config.is_active
    }))
  } catch (error) {
    console.error('Failed to fetch AI configs:', error)
    toastStore.showError('获取AI配置失败')
  } finally {
    loadingConfigs.value = false
  }
}

// 获取服务商显示名称
function getProviderDisplayName(provider) {
  const names = {
    deepseek: 'DeepSeek',
    qwen: '千问 (Qwen)',
    openai: 'OpenAI'
  }
  return names[provider] || provider
}

// 编辑配置
function editConfig(config) {
  editingConfig.value = config
  configForm.value = {
    provider: config.provider,
    apiKey: config.api_key,
    apiBase: config.api_base || '',
    model: config.model || ''
  }
  showAddConfigModal.value = true
}

// 关闭配置弹窗
function closeConfigModal() {
  showAddConfigModal.value = false
  editingConfig.value = null
  configForm.value = {
    provider: '',
    apiKey: '',
    apiBase: '',
    model: ''
  }
}

// 保存AI配置
async function saveAIConfig() {
  savingConfig.value = true
  try {
    const payload = {
      provider: configForm.value.provider,
      api_key: configForm.value.apiKey,
      api_base: configForm.value.apiBase || null,
      model: configForm.value.model || null
    }

    if (editingConfig.value) {
      await axios.put(`/api/ai/configs/${editingConfig.value.id}`, payload)
      toastStore.showSuccess('AI配置已更新')
    } else {
      await axios.post('/api/ai/configs', payload)
      toastStore.showSuccess('AI配置已添加')
    }

    closeConfigModal()
    await fetchAIConfigs()
  } catch (error) {
    console.error('Failed to save AI config:', error)
    toastStore.showError(error.response?.data?.detail || '保存失败，请重试')
  } finally {
    savingConfig.value = false
  }
}

// 激活配置
async function activateConfig(configId) {
  try {
    await axios.post(`/api/ai/configs/${configId}/activate`)
    toastStore.showSuccess('已激活该AI配置')
    await fetchAIConfigs()
  } catch (error) {
    console.error('Failed to activate config:', error)
    toastStore.showError('激活失败，请重试')
  }
}

// 确认删除配置
function confirmDeleteConfig(config) {
  if (confirm(`确定要删除${getProviderDisplayName(config.provider)}配置吗？`)) {
    deleteConfig(config.id)
  }
}

// 删除配置
async function deleteConfig(configId) {
  try {
    await axios.delete(`/api/ai/configs/${configId}`)
    toastStore.showSuccess('AI配置已删除')
    await fetchAIConfigs()
  } catch (error) {
    console.error('Failed to delete config:', error)
    toastStore.showError('删除失败，请重试')
  }
}

// 更新个人信息
async function handleUpdateProfile() {
  profileSubmitting.value = true
  try {
    await userApi.updateUserInfo(profileForm.value)
    userStore.setUserInfo(profileForm.value)
    toastStore.showSuccess('个人信息已更新')
  } catch (error) {
    console.error('Failed to update profile:', error)
    toastStore.showError('更新失败，请重试')
  } finally {
    profileSubmitting.value = false
  }
}

// 设置主题
function setTheme(theme) {
  userStore.setTheme(theme)
  toastStore.showSuccess(`已切换到${theme === 'dark' ? '深色' : '浅色'}模式`)
}

// 导出数据
async function exportData() {
  exporting.value = true
  try {
    const blob = await settingsApi.exportData()

    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `学迹_数据导出_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    window.URL.revokeObjectURL(url)

    toastStore.showSuccess('数据导出成功')
  } catch (error) {
    console.error('Failed to export data:', error)
    toastStore.showError('导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

// 清空缓存
async function clearCache() {
  if (!confirm('确定要清空应用缓存吗？')) return

  clearing.value = true
  try {
    await settingsApi.clearCache()

    // 清空本地缓存
    localStorage.removeItem('timerState')
    sessionStorage.clear()

    toastStore.showSuccess('缓存已清空')
  } catch (error) {
    console.error('Failed to clear cache:', error)
    toastStore.showError('操作失败，请重试')
  } finally {
    clearing.value = false
  }
}

// 确认删除所有数据
function confirmDeleteAll() {
  const confirmation = prompt('此操作将永久删除所有数据，请输入 "DELETE" 确认：')
  if (confirmation === 'DELETE') {
    toastStore.showError('演示版本不支持此操作')
  }
}
</script>
