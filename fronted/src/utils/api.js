import request from './request'

/**
 * 用户相关接口
 */
export const userApi = {
  // 获取用户信息
  getUserInfo() {
    return request.get('/user/info')
  },

  // 更新用户信息
  updateUserInfo(data) {
    return request.put('/user/info', data)
  },

  // 修改密码
  changePassword(data) {
    return request.post('/user/change-password', data)
  }
}

/**
 * 项目相关接口
 */
export const projectApi = {
  // 获取项目列表
  getProjectList(params) {
    return request.get('/projects', { params })
  },

  // 获取项目详情
  getProjectDetail(id) {
    return request.get(`/projects/${id}`)
  },

  // 创建项目
  createProject(data) {
    return request.post('/projects', data)
  },

  // 更新项目
  updateProject(id, data) {
    return request.put(`/projects/${id}`, data)
  },

  // 删除项目
  deleteProject(id) {
    return request.delete(`/projects/${id}`)
  },

  // 完成项目
  completeProject(id) {
    return request.post(`/projects/${id}/complete`)
  }
}

/**
 * 任务相关接口
 */
export const taskApi = {
  // 获取任务列表
  getTaskList(params) {
    return request.get('/tasks', { params })
  },

  // 获取任务详情
  getTaskDetail(id) {
    return request.get(`/tasks/${id}`)
  },

  // 创建任务
  createTask(data) {
    return request.post('/tasks', data)
  },

  // 更新任务
  updateTask(id, data) {
    return request.put(`/tasks/${id}`, data)
  },

  // 删除任务
  deleteTask(id) {
    return request.delete(`/tasks/${id}`)
  },

  // 开始计时
  startTimer(taskId) {
    return request.post(`/tasks/${taskId}/timer/start`)
  },

  // 暂停计时
  pauseTimer(taskId) {
    return request.post(`/tasks/${taskId}/timer/pause`)
  },

  // 结束计时
  stopTimer(taskId) {
    return request.post(`/tasks/${taskId}/timer/stop`)
  },

  // 获取当前计时状态
  getTimerStatus() {
    return request.get('/tasks/timer/status')
  },

  // 手动补录时间
  addManualTime(taskId, data) {
    return request.post(`/tasks/${taskId}/time-manual`, data)
  }
}

/**
 * 统计相关接口
 */
export const statisticsApi = {
  // 获取概览数据
  getOverview(params) {
    return request.get('/statistics/overview', { params })
  },

  // 获取项目时间分布
  getProjectTimeDistribution(params) {
    return request.get('/statistics/project-time', { params })
  },

  // 获取每日学习时长趋势
  getDailyTrend(params) {
    return request.get('/statistics/daily-trend', { params })
  },

  // 获取精力分配对比
  getEnergyDistribution(params) {
    return request.get('/statistics/energy', { params })
  }
}

/**
 * AI规划相关接口
 */
export const aiApi = {
  // 获取今日推荐任务
  getTodayRecommendations() {
    return request.get('/ai/recommendations')
  },

  // 获取精力预警
  getEnergyWarnings() {
    return request.get('/ai/warnings')
  },

  // 生成学习计划
  generatePlan(params) {
    return request.post('/ai/generate-plan', params)
  }
}

/**
 * 系统设置相关接口
 */
export const settingsApi = {
  // 导出数据
  exportData() {
    return request.get('/settings/export', { responseType: 'blob' })
  },

  // 清空缓存
  clearCache() {
    return request.post('/settings/clear-cache')
  },

  // 更新主题设置
  updateTheme(theme) {
    return request.put('/settings/theme', { theme })
  }
}
