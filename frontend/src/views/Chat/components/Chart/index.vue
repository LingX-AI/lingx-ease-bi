<script setup lang="ts">
import 'echarts'
import ECharts from 'vue-echarts'

interface IProps {
  option: Record<string, any>
}
withDefaults(defineProps<IProps>(), {})
const eChartsRef = ref()

defineExpose({
  getDataURL: (args: Record<string, any>) => eChartsRef.value?.getDataURL(args),
})
</script>

<template>
  <div class="w-full p-5 border border-border-1 rounded-[16px]">
    <ECharts
      v-if="option"
      ref="eChartsRef"
      :option="option"
      style="height: 400px"
    />
  </div>
</template>

<style lang="scss" scoped>

</style>
