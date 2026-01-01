<template>
  <div class="relative" :class="{ 'mb-4': margin }">
    <div class="flex items-center justify-between mb-2">
      <label v-if="label" class="text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ label }}
        <span v-if="required" class="text-danger">*</span>
      </label>
      <span class="text-sm font-semibold" :class="textColor">{{ modelValue }}%</span>
    </div>

    <div class="relative">
      <input
        type="range"
        :value="modelValue"
        @input="handleInput"
        :min="min"
        :max="max"
        :step="step"
        :disabled="disabled"
        class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider-thumb"
        :class="{ 'opacity-50 cursor-not-allowed': disabled }"
      />
      <div
        class="absolute top-1/2 -translate-y-1/2 left-0 h-2 rounded-lg pointer-events-none"
        :style="{
          width: percentage + '%',
          backgroundColor: color
        }"
      />
    </div>

    <p v-if="hint" class="mt-2 text-sm text-gray-500 dark:text-gray-400">
      {{ hint }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Number,
    default: 50
  },
  label: String,
  hint: String,
  min: {
    type: Number,
    default: 0
  },
  max: {
    type: Number,
    default: 100
  },
  step: {
    type: Number,
    default: 1
  },
  disabled: Boolean,
  required: Boolean,
  color: {
    type: String,
    default: '#4A90E2'
  },
  margin: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

const percentage = computed(() => {
  return ((props.modelValue - props.min) / (props.max - props.min)) * 100
})

const textColor = computed(() => {
  return { color: props.color }
})

function handleInput(e) {
  const value = parseInt(e.target.value)
  emit('update:modelValue', value)
}
</script>

<style scoped>
/* 自定义滑块样式 */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4A90E2;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: transform 0.15s ease;
}

input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

input[type="range"]::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4A90E2;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: transform 0.15s ease;
}

input[type="range"]::-moz-range-thumb:hover {
  transform: scale(1.1);
}

input[type="range"]:focus {
  outline: none;
}

input[type="range"]:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.3);
}

input[type="range"]:focus::-moz-range-thumb {
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.3);
}
</style>
