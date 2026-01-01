import { format, formatDistanceToNow, startOfWeek, endOfWeek, subDays } from 'date-fns'
import { zhCN } from 'date-fns/locale'

/**
 * 格式化日期
 * @param {Date|string|number} date - 日期
 * @param {string} formatStr - 格式字符串
 * @returns {string} 格式化后的日期
 */
export function formatDate(date, formatStr = 'yyyy-MM-dd') {
  return format(new Date(date), formatStr, { locale: zhCN })
}

/**
 * 格式化时间
 * @param {Date|string|number} date - 日期时间
 * @returns {string} 格式化后的时间
 */
export function formatTime(date) {
  return format(new Date(date), 'HH:mm:ss', { locale: zhCN })
}

/**
 * 格式化日期时间
 * @param {Date|string|number} date - 日期时间
 * @returns {string} 格式化后的日期时间
 */
export function formatDateTime(date) {
  return format(new Date(date), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN })
}

/**
 * 相对时间格式化
 * @param {Date|string|number} date - 日期
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(date) {
  return formatDistanceToNow(new Date(date), { locale: zhCN, addSuffix: true })
}

/**
 * 格式化时长（秒转时分秒）
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的时长
 */
export function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟${secs}秒`
  } else {
    return `${secs}秒`
  }
}

/**
 * 格式化时长（简短版）
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的时长
 */
export function formatDurationShort(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  } else if (minutes > 0) {
    return `${minutes}m`
  } else {
    return `${seconds}s`
  }
}

/**
 * 获取本周日期范围
 * @returns {object} 包含开始和结束日期的对象
 */
export function getWeekRange() {
  const now = new Date()
  return {
    start: startOfWeek(now, { locale: zhCN }),
    end: endOfWeek(now, { locale: zhCN })
  }
}

/**
 * 获取最近N天的日期
 * @param {number} days - 天数
 * @returns {Array} 日期数组
 */
export function getRecentDays(days = 7) {
  const result = []
  for (let i = days - 1; i >= 0; i--) {
    result.push(subDays(new Date(), i))
  }
  return result
}

/**
 * 获取星期几
 * @param {Date|string|number} date - 日期
 * @returns {string} 星期几
 */
export function getWeekday(date) {
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weekdays[new Date(date).getDay()]
}

/**
 * 格式化百分比
 * @param {number} value - 数值
 * @param {number} total - 总数
 * @returns {string} 百分比字符串
 */
export function formatPercent(value, total) {
  if (total === 0) return '0%'
  return `${Math.round((value / total) * 100)}%`
}

/**
 * 格式化数字（添加千分位）
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字
 */
export function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 获取问候语
 * @returns {string} 问候语
 */
export function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
}
