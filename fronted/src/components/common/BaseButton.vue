<template>
  <component
    :is="tag"
    :type="tag === 'button' ? nativeType : null"
    :to="tag === 'router-link' ? to : null"
    :href="tag === 'a' ? to : null"
    class="btn inline-flex items-center justify-center gap-2"
    :class="buttonClasses"
    :disabled="disabled || loading"
    v-bind="$attrs"
  ><i v-if="loading" class="fas fa-spinner animate-spin"></i><i v-else-if="icon" :class="icon"></i><slot></slot></component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 按钮类型
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger', 'ghost', 'ghost-danger'].includes(value)
  },
  // 按钮尺寸
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  // 原生类型
  nativeType: {
    type: String,
    default: 'button'
  },
  // 是否为块级按钮
  block: Boolean,
  // 图标
  icon: String,
  // 是否禁用
  disabled: Boolean,
  // 是否加载中
  loading: Boolean,
  // 链接地址
  to: String,
  // 标签类型
  tag: {
    type: String,
    default: 'button'
  }
})

const buttonClasses = computed(() => {
  const classes = []

  // 变体样式
  const variantClasses = {
    primary: 'btn-primary',
    success: 'btn-success',
    warning: 'btn-warning',
    danger: 'btn-danger',
    ghost: 'btn-ghost',
    'ghost-danger': 'bg-red-50 text-danger hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/30'
  }
  classes.push(variantClasses[props.variant])

  // 尺寸样式
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }
  classes.push(sizeClasses[props.size])

  // 块级样式
  if (props.block) {
    classes.push('w-full')
  }

  return classes
})
</script>
