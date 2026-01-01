<template>
  <div class="relative" :class="{ 'mb-4': margin }">
    <label
      v-if="label"
      class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5"
    >
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>

    <div class="relative">
      <span
        v-if="prefixIcon"
        class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
      >
        <i :class="prefixIcon"></i>
      </span>

      <input
        v-bind="$attrs"
        :value="modelValue"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        class="input"
        :class="inputClasses"
      />

      <span
        v-if="suffixIcon || loading"
        class="absolute right-3 top-1/2 -translate-y-1/2"
      ><i v-if="loading" class="fas fa-spinner animate-spin text-gray-400"></i><i v-else-if="suffixIcon" :class="suffixIcon"></i></span>
    </div>

    <p v-if="error" class="mt-1 text-sm text-danger">{{ error }}</p>
    <p v-else-if="hint" class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  error: String,
  hint: String,
  prefixIcon: String,
  suffixIcon: String,
  loading: Boolean,
  required: Boolean,
  margin: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const inputClasses = computed(() => {
  return {
    'pl-10': props.prefixIcon,
    'pr-10': props.suffixIcon || props.loading,
    'border-danger focus:ring-danger': props.error
  }
})

function handleInput(e) {
  emit('update:modelValue', e.target.value)
}

function handleBlur(e) {
  emit('blur', e)
}

function handleFocus(e) {
  emit('focus', e)
}
</script>
