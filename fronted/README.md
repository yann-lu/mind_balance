# 学迹 - 学习计划追踪系统

一个现代化的学习计划追踪系统，帮助用户管理学习项目、记录学习时长、并通过AI智能推荐优化学习计划。

## 技术栈

- **前端框架**: Vue 3 + Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **样式**: Tailwind CSS
- **图标**: Font Awesome
- **图表**: Chart.js + vue-chartjs
- **HTTP客户端**: Axios
- **日期处理**: date-fns

## 功能特性

### 核心功能
- **项目管理**: 创建、编辑、删除学习项目，设置精力占比
- **任务管理**: 添加任务、实时计时、手动补录时间
- **数据统计**: 可视化展示学习数据（环形图、柱状图、折线图）
- **AI规划**: 智能推荐任务、精力分配预警
- **主题切换**: 支持浅色/深色模式
- **响应式设计**: 完美适配手机、平板、PC

### UI/UX设计
- 清新护眼的配色方案
- 流畅的页面过渡动画
- 卡片化布局设计
- 移动端友好的交互体验

## 项目结构

```
learning-tracker/
├── public/              # 静态资源
├── src/
│   ├── assets/          # 资源文件
│   ├── components/      # 组件
│   │   ├── common/      # 通用组件
│   │   └── layout/      # 布局组件
│   ├── router/          # 路由配置
│   ├── store/           # Pinia状态管理
│   ├── styles/          # 全局样式
│   ├── utils/           # 工具函数
│   ├── views/           # 页面组件
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html           # HTML模板
├── package.json         # 项目配置
├── vite.config.js       # Vite配置
├── tailwind.config.js   # Tailwind配置
└── README.md            # 项目说明
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 配色方案

| 颜色名称 | 色值 | 用途 |
|---------|------|------|
| 主色 | #4A90E2 | 按钮、标题、进度条 |
| 成功色 | #66BB6A | 成功状态 |
| 警告色 | #FF9800 | 警告/暂停 |
| 危险色 | #E53935 | 错误/高优先级 |
| 背景色 | #F5F7FA | 页面背景 |
| 卡片色 | #FFFFFF | 卡片背景 |

## API接口说明

项目假设后端API遵循以下格式：

### 项目相关
- `GET /api/projects` - 获取项目列表
- `GET /api/projects/:id` - 获取项目详情
- `POST /api/projects` - 创建项目
- `PUT /api/projects/:id` - 更新项目
- `DELETE /api/projects/:id` - 删除项目
- `POST /api/projects/:id/complete` - 完成项目

### 任务相关
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/:id` - 获取任务详情
- `POST /api/tasks` - 创建任务
- `PUT /api/tasks/:id` - 更新任务
- `DELETE /api/tasks/:id` - 删除任务
- `POST /api/tasks/:id/timer/start` - 开始计时
- `POST /api/tasks/:id/timer/pause` - 暂停计时
- `POST /api/tasks/:id/timer/stop` - 结束计时
- `POST /api/tasks/:id/time-manual` - 手动补录时间

### 统计相关
- `GET /api/statistics/overview` - 获取概览数据
- `GET /api/statistics/project-time` - 获取项目时间分布
- `GET /api/statistics/daily-trend` - 获取每日趋势
- `GET /api/statistics/energy` - 获取精力分配

### AI相关
- `GET /api/ai/recommendations` - 获取推荐任务
- `GET /api/ai/energy-warnings` - 获取精力预警
- `POST /api/ai/generate-plan` - 生成学习计划

## 开发说明

### 添加新页面

1. 在 `src/views/` 下创建页面组件
2. 在 `src/router/index.js` 中添加路由配置
3. 在侧边栏 `src/components/layout/Sidebar.vue` 中添加菜单项

### 修改主题配色

编辑 `tailwind.config.js` 中的 `theme.extend.colors` 配置。

### 添加新API接口

在 `src/utils/api.js` 中添加对应的API方法。

## 浏览器支持

- Chrome (最新版本)
- Firefox (最新版本)
- Safari (最新版本)
- Edge (最新版本)

## 许可证

MIT License

## 作者

学迹开发团队 © 2025
