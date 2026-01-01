<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-text-primary dark:text-text-dark">任务管理</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">管理你的学习任务，记录学习时长</p>
      </div>
      <BaseButton variant="primary" @click="openCreateModal">
        <i class="fas fa-plus"></i>
        新建任务
      </BaseButton>
    </div>

    <div class="card p-4">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex items-center gap-2">
          <button
            v-for="tab in statusTabs"
            :key="tab.value"
            @click="activeStatus = tab.value"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            :class="activeStatus === tab.value ? 'bg-primary text-white' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
          >
            {{ tab.label }}
            <span v-if="tab.count !== undefined" class="ml-1 opacity-70">({{ tab.count }})</span>
          </button>
        </div>

        <div class="ml-auto flex items-center gap-3">
          <select v-model="selectedProject" class="input py-1.5 text-sm pr-8">
            <option value="">全部项目</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
          </select>
          <div class="relative">
            <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
            <input v-model="searchQuery" type="text" placeholder="搜索任务..." class="input pl-9 py-1.5 text-sm w-48">
          </div>
        </div>
      </div>
    </div>

    <div v-if="timerStore.currentTask" class="card p-5 bg-gradient-to-r from-primary to-primary-hover text-white">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <p class="text-sm text-white/70 mb-1">正在学习</p>
          <h3 class="text-xl font-bold">{{ timerStore.currentTask.name }}</h3>
          <p class="text-sm text-white/70">{{ timerStore.currentTask.projectName }}</p>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-center">
            <p class="text-4xl font-mono font-bold">{{ timerStore.formattedTime }}</p>
            <p class="text-xs text-white/70 mt-1">本次时长</p>
          </div>
          <div class="flex flex-col gap-2">
            <button v-if="timerStore.isRunning" @click="pauseTimer" class="btn px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg"><i class="fas fa-pause mr-2"></i>暂停</button>
            <button v-else @click="resumeTimer" class="btn px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg"><i class="fas fa-play mr-2"></i>继续</button>
            <button @click="stopTimer" class="btn px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg"><i class="fas fa-stop mr-2"></i>结束</button>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-4">
      <div v-if="loading" class="grid gap-3">
        <div v-for="i in 5" :key="i" class="card p-4">
          <div class="skeleton h-5 w-1/3 rounded mb-2"></div>
          <div class="skeleton h-4 w-1/4 rounded"></div>
        </div>
      </div>

      <div v-if="!loading && filteredTasks.length > 0" class="space-y-3">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="card p-4 group hover:border-primary/30 border-2 border-transparent transition-all"
          :class="{ 'ring-2 ring-primary': timerStore.currentTask?.id === task.id }"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-3 flex-1 min-w-0">
              <div
                class="w-3 h-3 rounded-full mt-1.5 flex-shrink-0"
                :class="{'bg-gray-300': task.status === 'pending', 'bg-primary animate-pulse': task.status === 'in_progress' && timerStore.currentTask?.id === task.id, 'bg-primary': task.status === 'in_progress' && timerStore.currentTask?.id !== task.id, 'bg-success': task.status === 'completed'}"
              ></div>
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-text-primary dark:text-text-dark truncate">{{ task.name }}</h3>
                <div class="flex flex-wrap items-center gap-3 mt-1.5">
                  <span class="text-sm text-gray-500 dark:text-gray-400"><i class="fas fa-folder mr-1"></i>{{ task.projectName }}</span>
                  <span v-if="task.totalDuration > 0" class="text-sm text-gray-500 dark:text-gray-400"><i class="fas fa-clock mr-1"></i>{{ formatDurationShort(task.totalDuration) }}</span>
                  <span class="badge" :class="{'badge-primary': task.status === 'pending', 'badge-warning': task.status === 'in_progress', 'badge-success': task.status === 'completed'}">{{ statusLabels[task.status] }}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <template v-if="task.status !== 'completed'">
                <button v-if="timerStore.currentTask?.id === task.id" @click="handleTaskAction(task)" class="p-2 rounded-lg transition-all" :class="timerStore.isRunning ? 'bg-warning/10 text-warning' : 'bg-success/10 text-success'"><i :class="timerStore.isRunning ? 'fas fa-pause' : 'fas fa-play'"></i></button>
                <button v-else-if="timerStore.currentTask?.id !== task.id" @click="startTask(task)" class="p-2 rounded-lg bg-primary/10 text-primary transition-all"><i class="fas fa-play"></i></button>
                <button @click="openAddTimeModal(task)" class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 transition-all"><i class="fas fa-plus-circle"></i></button>
              </template>
              <button @click="openEditModal(task)" class="p-2 rounded-lg opacity-0 group-hover:opacity-100 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 transition-all"><i class="fas fa-edit"></i></button>
              <button @click="confirmDelete(task)" class="p-2 rounded-lg opacity-0 group-hover:opacity-100 bg-red-50 dark:bg-red-900/20 text-danger transition-all"><i class="fas fa-trash"></i></button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!loading && filteredTasks.length === 0" class="card p-12 text-center">
        <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center"><i class="fas fa-tasks text-3xl text-gray-400"></i></div>
        <h3 class="text-lg font-semibold text-text-primary dark:text-text-dark mb-2">{{ searchQuery || selectedProject ? '没有找到匹配的任务' : '还没有任务' }}</h3>
        <p v-if="!searchQuery && !selectedProject" class="text-sm text-gray-500 dark:text-gray-400 mb-4">创建你的第一个学习任务吧</p>
        <BaseButton v-if="!searchQuery && !selectedProject" variant="primary" @click="openCreateModal"><i class="fas fa-plus"></i>创建任务</BaseButton>
      </div>
    </div>

    <BaseModal :is-open="modalOpen" :title="editingTask ? '编辑任务' : '新建任务'" @close="closeModal">
      <form id="taskForm" @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">所属项目 <span class="text-danger">*</span></label>
          <select v-model="formData.projectId" class="input" required>
            <option value="">请选择项目</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
          </select>
        </div>
        <BaseInput v-model="formData.name" label="任务名称" placeholder="例如：复习第三章内容" required :error="errors.name" />
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">优先级</label>
          <div class="flex gap-2">
            <button v-for="priority in priorityOptions" :key="priority.value" type="button" @click="formData.priority = priority.value" class="flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all" :class="formData.priority === priority.value ? priority.activeClass : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'">{{ priority.label }}</button>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">任务描述（可选）</label>
          <textarea v-model="formData.description" placeholder="添加任务备注..." rows="3" class="input resize-none"></textarea>
        </div>
      </form>
      <template #footer>
        <BaseButton variant="ghost" type="button" @click="closeModal">取消</BaseButton>
        <BaseButton variant="primary" form="taskForm" type="submit" :loading="submitting">{{ editingTask ? '保存' : '创建' }}</BaseButton>
      </template>
    </BaseModal>

    <BaseModal :is-open="addTimeModalOpen" title="手动补录时间" @close="closeAddTimeModal">
      <form id="addTimeForm" @submit.prevent="handleAddTime">
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">为「{{ addingTimeTask?.name }}」补录学习时长</p>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">学习时长</label>
          <div class="flex items-center gap-3">
            <div class="flex-1"><label class="block text-xs text-gray-500 mb-1">小时</label><input v-model.number="addTimeData.hours" type="number" min="0" max="23" class="input text-center"></div>
            <span class="text-gray-400 mt-5">:</span>
            <div class="flex-1"><label class="block text-xs text-gray-500 mb-1">分钟</label><input v-model.number="addTimeData.minutes" type="number" min="0" max="59" class="input text-center"></div>
          </div>
        </div>
        <BaseInput v-model="addTimeData.note" label="备注（可选）" placeholder="例如：完成了第三章的练习" :margin="false" />
      </form>
      <template #footer>
        <BaseButton variant="ghost" type="button" @click="closeAddTimeModal">取消</BaseButton>
        <BaseButton variant="primary" form="addTimeForm" type="submit" :loading="addTimeSubmitting">确定</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { BaseModal, BaseButton, BaseInput } from '@/components/common'
import { taskApi, projectApi } from '@/utils/api'
import { formatDurationShort, formatDuration } from '@/utils/format'
import { useTimerStore } from '@/store/timer'
import { useToastStore } from '@/store/toast'

const timerStore = useTimerStore()
const toastStore = useToastStore()
const tasks = ref([])
const projects = ref([])
const loading = ref(false)
const modalOpen = ref(false)
const editingTask = ref(null)
const submitting = ref(false)
const activeStatus = ref('all')
const selectedProject = ref('')
const searchQuery = ref('')
const formData = ref({ projectId: '', name: '', priority: 'medium', description: '' })
const errors = ref({})
const addTimeModalOpen = ref(false)
const addingTimeTask = ref(null)
const addTimeSubmitting = ref(false)
const addTimeData = ref({ hours: 0, minutes: 0, note: '' })

const priorityOptions = [
  { value: 'high', label: '高', activeClass: 'bg-red-100 text-red-600 dark:bg-red-900/30' },
  { value: 'medium', label: '中', activeClass: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30' },
  { value: 'low', label: '低', activeClass: 'bg-green-100 text-green-600 dark:bg-green-900/30' }
]
const statusLabels = { pending: '未开始', in_progress: '进行中', completed: '已完成' }
const statusTabs = computed(() => [
  { label: '全部', value: 'all', count: tasks.value.length },
  { label: '未开始', value: 'pending', count: tasks.value.filter(t => t.status === 'pending').length },
  { label: '进行中', value: 'in_progress', count: tasks.value.filter(t => t.status === 'in_progress').length },
  { label: '已完成', value: 'completed', count: tasks.value.filter(t => t.status === 'completed').length }
])

const filteredTasks = computed(() => {
  let result = tasks.value
  if (activeStatus.value !== 'all') result = result.filter(t => t.status === activeStatus.value)
  if (selectedProject.value) result = result.filter(t => t.projectId === selectedProject.value)
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t => t.name.toLowerCase().includes(query) || (t.description && t.description.toLowerCase().includes(query)))
  }
  return result
})

async function fetchTasks() {
  loading.value = true
  try {
    const data = await taskApi.getTaskList()
    tasks.value = (data || []).map(t => ({ id: t.id, name: t.title, projectId: t.project_id, projectName: t.project_name, status: t.status, priority: t.priority, totalDuration: t.total_duration, description: t.description }))
  } catch (error) {
    tasks.value = []
  } finally {
    loading.value = false
  }
}

async function fetchProjects() {
  try {
    const data = await projectApi.getProjectList()
    projects.value = data || []
  } catch (error) {}
}

async function startTask(task) {
  if (timerStore.currentTask?.id === task.id) return
  timerStore.startTimer(task)
  try {
    await taskApi.startTimer(task.id)
    fetchTasks()
  } catch (error) {}
}

function handleTaskAction(task) {
  if (timerStore.isRunning) pauseTimer()
  else resumeTimer()
}

async function pauseTimer() {
  timerStore.pauseTimer()
  try { await taskApi.pauseTimer(timerStore.currentTask.id) } catch (error) {}
}

async function resumeTimer() {
  timerStore.resumeTimer()
  try { await taskApi.startTimer(timerStore.currentTask.id) } catch (error) {}
}

async function stopTimer() {
  const { task, time } = timerStore.stopTimer()
  try {
    await taskApi.stopTimer(task.id)
    fetchTasks()
  } catch (error) {}
}

function openCreateModal() {
  editingTask.value = null
  formData.value = { projectId: selectedProject.value || '', name: '', priority: 'medium', description: '' }
  errors.value = {}
  modalOpen.value = true
}

function openEditModal(task) {
  editingTask.value = task
  formData.value = { projectId: task.projectId, name: task.name, priority: task.priority || 'medium', description: task.description || '' }
  errors.value = {}
  modalOpen.value = true
}

function closeModal() {
  modalOpen.value = false
  editingTask.value = null
  errors.value = {}
}

function validateForm() {
  errors.value = {}
  if (!formData.value.projectId) errors.value.projectId = '请选择所属项目'
  if (!formData.value.name.trim()) errors.value.name = '请输入任务名称'
  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  if (!validateForm()) return
  submitting.value = true
  try {
    const payload = { project_id: formData.value.projectId, title: formData.value.name, priority: formData.value.priority, description: formData.value.description }
    if (editingTask.value) await taskApi.updateTask(editingTask.value.id, payload)
    else await taskApi.createTask(payload)
    toastStore.showSuccess(editingTask.value ? '任务更新成功' : '任务创建成功')
    closeModal()
    fetchTasks()
  } catch (error) {
    toastStore.showError('操作失败')
  } finally {
    submitting.value = false
  }
}

function openAddTimeModal(task) {
  addingTimeTask.value = task
  addTimeData.value = { hours: 0, minutes: 0, note: '' }
  addTimeModalOpen.value = true
}

function closeAddTimeModal() {
  addTimeModalOpen.value = false
  addingTimeTask.value = null
}

async function handleAddTime() {
  const totalSeconds = addTimeData.value.hours * 3600 + addTimeData.value.minutes * 60
  if (totalSeconds <= 0) return
  addTimeSubmitting.value = true
  try {
    await taskApi.addManualTime(addingTimeTask.value.id, { duration: totalSeconds, note: addTimeData.value.note })
    toastStore.showSuccess('补录成功')
    closeAddTimeModal()
    fetchTasks()
  } catch (error) {
    toastStore.showError('失败')
  } finally {
    addTimeSubmitting.value = false
  }
}

async function confirmDelete(task) {
  if (confirm(`确定要删除「${task.name}」吗？`)) {
    try {
      await taskApi.deleteTask(task.id)
      toastStore.showSuccess('任务已删除')
      fetchTasks()
    } catch (error) {
      toastStore.showError('删除失败')
    }
  }
}

onMounted(() => {
  fetchProjects()
  fetchTasks()
})
</script>