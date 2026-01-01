<template>
  <div class="min-h-[60vh] flex items-center justify-center">
    <div class="text-center">
      <div class="w-32 h-32 mx-auto mb-6 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
        <i class="fas fa-exclamation-triangle text-6xl text-gray-400"></i>
      </div>
      <h1 class="text-2xl font-bold text-text-primary dark:text-text-dark mb-2">
        404
      </h1>
      <p class="text-gray-500 dark:text-gray-400 mb-6">
        抱歉，您访问的页面不存在
      </p>
      <router-link
        to="/"
        class="btn btn-primary"
      >
        <i class="fas fa-home mr-2"></i>返回首页
      </router-link>
    </div>
  </div>
</template>
