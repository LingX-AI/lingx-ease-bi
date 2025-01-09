<script setup lang="ts">
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  StopOutlined,
} from '@ant-design/icons-vue'
import type { IStep } from '@/types/chat'
import { EStepStatus } from '@/types/chat'

interface IProps {
  step: IStep
}
withDefaults(defineProps<IProps>(), {})
</script>

<template>
  <div class="mr-3">
    <a-spin
      v-if="step?.status === EStepStatus.IN_PROGRESS"
      size="small"
    />
    <CheckCircleOutlined
      v-else-if="step?.status === EStepStatus.COMPLETED"
      style="font-size:14px;color:#4CAF50"
    />
    <ExclamationCircleOutlined
      v-else-if="step?.status === EStepStatus.ERROR"
      style="font-size:14px;color:#FF9800"
    />
    <StopOutlined
      v-else-if="step?.status === EStepStatus.CANCELLED"
      style="font-size:14px;color:#FF9800"
    />
  </div>
</template>

<style scoped lang="scss">
</style>
