<script setup lang="ts">
import type { Ref } from 'vue'
import { useMessage } from '@/composables/specific'
import MessageHistory from '@/views/Chat/components/MessageHistory/index.vue'

const { t } = useI18n()
const question = ref('')
const applicationId = inject('applicationId') as string
const isPendingResponse = inject('isPendingResponse') as Ref<boolean>
const showMessageHistory = ref(false)
const {
  chat,
  cancelChat,
} = useMessage({ isPendingResponse })

const handleSend = async () => {
  await chat(applicationId, question, true)
}

const handleCancel = () => {
  isPendingResponse.value = false
  cancelChat()
}
</script>

<template>
  <div class="flex justify-between items-center w-full pl-4 p-3 border border-border-1 rounded-[12px] focus-within:border-primary">
    <a-tooltip>
      <template #title>
        {{ t('chat.chartHistory') }}
      </template>
      <span
        class="iconfont icon-history text-[#212328] text-[24px] cursor-pointer"
        @click="showMessageHistory = true"
      />
    </a-tooltip>
    <div class="w-[1px] h-6 mx-4 bg-border-1" />
    <a-textarea
      v-model:value="question"
      class="px-0 mr-4"
      :allowClear="false"
      autoSize
      :bordered="false"
      :placeholder="t('chat.askQuestion')"
      @press-enter.stop.prevent="handleSend"
    />
    <div
      v-if="!isPendingResponse"
      class="flex-center flex-shrink-0 w-10 h-10 rounded-[8px] text-white"
      :class="question.trim() ? 'bg-primary cursor-pointer' : 'bg-[#d9e1e6] cursor-not-allowed'"
      @click="handleSend"
    >
      <span class="iconfont icon-send text-[#FFFFFF] text-[20px] cursor-pointer" />
    </div>
    <div
      v-else
      class="flex-center flex-shrink-0 w-10 h-10 text-primary rounded-[8px] cursor-pointer bg-white"
      @click="handleCancel"
    >
      <span class="iconfont icon-stop text-[40px] cursor-pointer" />
    </div>
  </div>
  <MessageHistory
    v-if="showMessageHistory"
    @closed="showMessageHistory = false"
  />
</template>

<style lang="scss" scoped>
</style>
