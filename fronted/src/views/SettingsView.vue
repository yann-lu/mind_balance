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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { BaseInput, BaseButton } from '@/components/common'
import { useUserStore } from '@/store/user'
import { useToastStore } from '@/store/toast'
import { userApi, settingsApi } from '@/utils/api'

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

// 初始化表单
onMounted(() => {
  profileForm.value = {
    username: userStore.userInfo?.username || '',
    email: userStore.userInfo?.email || ''
  }
})

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
