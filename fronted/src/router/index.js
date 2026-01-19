import { createRouter, createWebHistory } from 'vue-router'
import { MainLayout } from '@/components/layout'
import { useUserStore } from '@/store/user'

// 页面组件（懒加载）
const HomeView = () => import('@/views/HomeView.vue')
const ProjectsView = () => import('@/views/ProjectsView.vue')
const TasksView = () => import('@/views/TasksView.vue')
const StatisticsView = () => import('@/views/StatisticsView.vue')
const AIPlanningView = () => import('@/views/AIPlanningView.vue')
const SettingsView = () => import('@/views/SettingsView.vue')

// 路由配置
const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: HomeView,
        meta: { title: '首页' }
      },
      {
        path: 'projects',
        name: 'projects',
        component: ProjectsView,
        meta: { title: '项目管理' }
      },
      {
        path: 'projects/:id',
        name: 'project-detail',
        component: ProjectsView,
        meta: { title: '项目详情' }
      },
      {
        path: 'tasks',
        name: 'tasks',
        component: TasksView,
        meta: { title: '任务管理' }
      },
      {
        path: 'statistics',
        name: 'statistics',
        component: StatisticsView,
        meta: { title: '数据统计' }
      },
      {
        path: 'ai-planning',
        name: 'ai-planning',
        component: AIPlanningView,
        meta: { title: 'AI规划' }
      },
      {
        path: 'settings',
        name: 'settings',
        component: SettingsView,
        meta: { title: '设置' }
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '页面不存在' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  const title = to.meta.title || '学迹'
  document.title = `${title} - 学迹`

  // 这里可以添加登录验证逻辑
  // const userStore = useUserStore()
  // if (!userStore.userInfo && to.path !== '/login') {
  //   next('/login')
  //   return
  // }

  next()
})

export default router
