<script setup lang="ts">
import { computed } from 'vue'

interface IProps {
  size?: 'small' | 'default' | 'large'
  color?: string
}

const props = withDefaults(defineProps<IProps>(), {
  size: 'default',
  color: '#78909C',
})

const wh = computed(() => {
  switch (props.size) {
    case 'small':
      return '3px'
    case 'large':
      return '9px'
    default:
      return '6px'
  }
})

const margin = computed(() => {
  switch (props.size) {
    case 'small':
      return '2px'
    case 'large':
      return '3px'
    default:
      return '3px'
  }
})
</script>

<template>
  <div class="loading-container">
    <span class="dot" />
    <span class="dot" />
    <span class="dot" />
  </div>
</template>

<style scoped lang="scss">
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.dot {
  background-color: #ccc;
  width: v-bind('wh');
  height: v-bind('wh');
  border-radius: 50%;
  margin: 0 v-bind('margin');
  animation: loadingDots 1.5s infinite ease-in-out;
}

@keyframes loadingDots {
  0%, 80%, 100% {
    background-color: #ccc;
  }
  40% {
    background-color: v-bind('color');
  }
}

.dot:nth-child(1) {
  animation-delay: 0s;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}
</style>
