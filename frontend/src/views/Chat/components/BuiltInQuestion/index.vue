<script setup lang="ts">
import type { Ref } from 'vue'
import { useMessage } from '@/composables/specific'
import type { IAppSuggestedQuestion } from '@/types/app'

interface IProps {
  applicationId: string
}

const { applicationId } = defineProps<IProps>()

const { t } = useI18n()
const questions = ref<string[]>([])
const isPendingResponse = inject('isPendingResponse') as Ref<boolean>
const { getSuggestedQuestions } = useAppDatabase()
const { chat } = useMessage({ isPendingResponse })
const init = async () => {
  const _questions = await getSuggestedQuestions(applicationId)
  questions.value = _questions.map((item: IAppSuggestedQuestion) => item.question)
}
init()
const handleSend = async (question: string) => {
  await chat(applicationId, question, true)
}
</script>

<template>
  <div class="mb-8">
    <template v-if="questions.length">
      <p class="text-[18px] font-[600] text-text-1 text-center mb-8">
        {{ t('chat.wantKnow') }}
      </p>
      <div class="flex justify-center flex-wrap mb-[80px]">
        <div
          v-for="(question, index) in questions"
          :key="index"
          class="mx-[27px] border border-border-1 rounded-[12px] w-[246px] cursor-pointer hover:bg-[#04346107]"
          @click="handleSend(question)"
        >
          <div class="flex justify-between items-center py-[10px] px-[20px] border-b border-border-1">
            <span class="iconfont icon-tip text-[#696974] text-[24px]" />
            <span class="iconfont icon-arrow-right text-[#212328] text-[24px]" />
          </div>
          <div class="p-4 leading-[22px] text-[14px] text-text-1">
            {{ question }}
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style lang="scss" scoped></style>
