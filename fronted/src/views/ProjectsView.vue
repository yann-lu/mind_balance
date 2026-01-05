<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-text-primary dark:text-text-dark">项目管理</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">管理你的学习项目，设置精力占比</p>
      </div>
      <BaseButton variant="primary" @click="openCreateModal">
        <i class="fas fa-plus"></i>
        新建项目
      </BaseButton>
    </div>

    <div class="card p-4">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex items-center gap-2">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            @click="activeTab = tab.value"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            :class="activeTab === tab.value ? 'bg-primary text-white' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
          >
            {{ tab.label }}
            <span v-if="tab.count !== undefined" class="ml-1 opacity-70">({{ tab.count }})</span>
          </button>
        </div>

        <div class="ml-auto flex items-center gap-2">
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索项目..."
              class="input pl-9 py-1.5 text-sm w-48"
            >
          </div>
        </div>
      </div>
    </div>

    <div class="mt-4">
      <div v-if="loading" class="grid gap-4">
        <div v-for="i in 3" :key="i" class="card p-5">
          <div class="skeleton h-6 w-1/3 rounded mb-3"></div>
          <div class="skeleton h-4 w-1/2 rounded mb-4"></div>
          <div class="skeleton h-2 w-full rounded"></div>
        </div>
      </div>

      <div v-if="!loading && filteredProjects.length > 0" class="grid gap-4">
        <div
          v-for="project in filteredProjects"
          :key="project.id"
          class="card p-5 group hover:border-primary/30 border-2 border-transparent transition-all"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-4">
              <div
                class="w-12 h-12 rounded-xl flex items-center justify-center"
                :style="{ backgroundColor: project.color + '20' }"
              >
                <i :class="project.icon" class="text-2xl" :style="{ color: project.color }"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-text-primary dark:text-text-dark">
                  {{ project.name }}
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ project.description || '暂无描述' }}</p>
              </div>
            </div>

            <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="openEditModal(project)" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300">
                <i class="fas fa-edit"></i>
              </button>
              <button v-if="!project.isCompleted" @click="confirmComplete(project)" class="p-2 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 text-success">
                <i class="fas fa-check"></i>
              </button>
              <button @click="confirmDelete(project)" class="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-danger">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>

          <div class="grid sm:grid-cols-3 gap-4 mb-4">
            <div class="flex items-center gap-2 text-sm">
              <i class="fas fa-tasks text-gray-400"></i>
              <span class="text-gray-600 dark:text-gray-300">{{ project.completedTasks }}/{{ project.totalTasks }} 个任务</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <i class="fas fa-clock text-gray-400"></i>
              <span class="text-gray-600 dark:text-gray-300">{{ formatDurationShort(project.totalDuration) }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <span class="badge" :class="project.isCompleted ? 'badge-success' : 'badge-primary'">
                {{ project.isCompleted ? '已完成' : '进行中' }}
              </span>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-gray-600 dark:text-gray-300">目标精力占比</span>
              <span class="font-semibold" :style="{ color: project.color }">{{ project.energyPercent }}%</span>
            </div>
            <div class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-300" :style="{ width: project.energyPercent + '%', backgroundColor: project.color }"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!loading && filteredProjects.length === 0" class="card p-12 text-center">
        <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
          <i class="fas fa-folder-open text-3xl text-gray-400"></i>
        </div>
        <h3 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-2">
          {{ searchQuery ? '没有找到匹配的项目' : '还没有项目' }}
        </h3>
        <p v-if="!searchQuery" class="text-sm text-gray-500 dark:text-gray-400 mb-4">创建你的第一个学习项目吧</p>
        <BaseButton v-if="!searchQuery" variant="primary" @click="openCreateModal">
          <i class="fas fa-plus"></i>
          创建项目
        </BaseButton>
      </div>
    </div>

    <BaseModal
      :is-open="modalOpen"
      :title="editingProject ? '编辑项目' : '新建项目'"
      @close="closeModal"
    >
      <form id="projectForm" @submit.prevent="handleSubmit">
        <BaseInput v-model="formData.name" label="项目名称" placeholder="例如：Python学习" required :error="errors.name" />
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">项目图标</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="icon in iconOptions"
              :key="icon.value"
              type="button"
              @click="formData.icon = icon.value"
              class="w-10 h-10 rounded-lg flex items-center justify-center transition-all"
              :class="formData.icon === icon.value ? 'bg-primary text-white ring-2 ring-primary ring-offset-2' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'"
            ><i :class="icon.value"></i></button>
          </div>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">项目颜色</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="color in colorOptions"
              :key="color"
              type="button"
              @click="formData.color = color"
              class="w-8 h-8 rounded-lg transition-all"
              :class="formData.color === color ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : 'hover:scale-105'"
              :style="{ backgroundColor: color }"
            ></button>
          </div>
        </div>
        <BaseSlider v-model="formData.energyPercent" label="目标精力占比" :min="0" :max="100" :color="formData.color" hint="该项目在你的学习计划中的目标时间分配比例" />
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">项目描述（可选）</label>
          <textarea v-model="formData.description" placeholder="简单描述这个学习项目..." rows="3" class="input resize-none"></textarea>
        </div>
      </form>
      <template #footer>
        <BaseButton variant="ghost" type="button" @click="closeModal">取消</BaseButton>
        <BaseButton variant="primary" form="projectForm" type="submit" :loading="submitting">{{ editingProject ? '保存' : '创建' }}</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { BaseModal, BaseButton, BaseInput, BaseSlider } from '@/components/common'
import { projectApi } from '@/utils/api'
import { formatDurationShort } from '@/utils/format'
import { useToastStore } from '@/store/toast'

const toastStore = useToastStore()
const projects = ref([])
const loading = ref(false)
const modalOpen = ref(false)
const editingProject = ref(null)
const submitting = ref(false)
const activeTab = ref('active')
const searchQuery = ref('')
const formData = ref({ name: '', icon: 'fas fa-book', color: '#4A90E2', energyPercent: 50, description: '' })
const errors = ref({})

const iconOptions = [
  { value: 'fas fa-book', label: '书籍' }, { value: 'fas fa-code', label: '代码' },
  { value: 'fas fa-language', label: '语言' }, { value: 'fas fa-calculator', label: '数学' },
  { value: 'fas fa-flask', label: '科学' }, { value: 'fas fa-music', label: '音乐' },
  { value: 'fas fa-palette', label: '艺术' }, { value: 'fas fa-dumbbell', label: '运动' },
  { value: 'fab fa-python', label: 'Python' }, { value: 'fab fa-js', label: 'JavaScript' },
  { value: 'fab fa-java', label: 'Java' }, { value: 'fas fa-database', label: '数据库' }
]
const colorOptions = ['#4A90E2', '#66BB6A', '#FF9800', '#E53935', '#9C27B0', '#00BCD4', '#FFC107', '#8BC34A', '#FF5722', '#607D8B', '#3F51B5', '#009688']

const tabs = computed(() => [
  { label: '全部', value: 'all', count: projects.value.length },
  { label: '进行中', value: 'active', count: projects.value.filter(p => !p.isCompleted).length },
  { label: '已完成', value: 'completed', count: projects.value.filter(p => p.isCompleted).length }
])

const filteredProjects = computed(() => {
  let result = projects.value
  if (activeTab.value === 'active') result = result.filter(p => !p.isCompleted)
  else if (activeTab.value === 'completed') result = result.filter(p => p.isCompleted)
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p => p.name.toLowerCase().includes(query) || (p.description && p.description.toLowerCase().includes(query)))
  }
  return result
})

async function fetchProjects() {
  loading.value = true
  try {
    const data = await projectApi.getProjectList()
    projects.value = (data || []).map(p => ({
      id: p.id, name: p.name, description: p.description, icon: p.icon, color: p.color_hex,
      energyPercent: p.energy_percent, totalTasks: p.total_tasks, completedTasks: p.completed_tasks,
      totalDuration: p.total_duration, isCompleted: p.is_completed
    }))
  } catch (error) {
    console.error('Failed to fetch projects:', error)
    projects.value = []
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  editingProject.value = null
  formData.value = { name: '', icon: 'fas fa-book', color: '#4A90E2', energyPercent: 50, description: '' }
  errors.value = {}
  modalOpen.value = true
}

function openEditModal(project) {
  editingProject.value = project
  formData.value = { name: project.name, icon: project.icon, color: project.color, energyPercent: project.energyPercent, description: project.description || '' }
  errors.value = {}
  modalOpen.value = true
}

function closeModal() {
  modalOpen.value = false
  editingProject.value = null
  errors.value = {}
}

function validateForm() {
  errors.value = {}
  if (!formData.value.name.trim()) errors.value.name = '请输入项目名称'
  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  if (!validateForm()) return
  submitting.value = true
  try {
    const payload = { name: formData.value.name, icon: formData.value.icon, color_hex: formData.value.color, energy_percent: formData.value.energyPercent, description: formData.value.description }
    if (editingProject.value) await projectApi.updateProject(editingProject.value.id, payload)
    else await projectApi.createProject(payload)
    toastStore.showSuccess(editingProject.value ? '项目更新成功' : '项目创建成功')
    closeModal()
    fetchProjects()
  } catch (error) {
    toastStore.showError('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

async function confirmComplete(project) {
  if (confirm(`确定要标记「${project.name}」为完成吗？`)) {
    try {
      await projectApi.completeProject(project.id)
      toastStore.showSuccess('项目已标记为完成')
      fetchProjects()
    } catch (error) {
      toastStore.showError('操作失败，请重试')
    }
  }
}

async function confirmDelete(project) {
  if (confirm(`确定要删除「${project.name}」吗？此操作不可恢复。`)) {
    try {
      await projectApi.deleteProject(project.id)
      toastStore.showSuccess('项目已删除')
      fetchProjects()
    } catch (error) {
      toastStore.showError('删除失败，请重试')
    }
  }
}

onMounted(fetchProjects)
</script>
