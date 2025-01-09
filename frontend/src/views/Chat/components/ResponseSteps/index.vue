<script setup lang="ts">
import {
  CaretRightOutlined,
} from '@ant-design/icons-vue'
import StepStatus from '../StepStatus/index.vue'
import type { IStep } from '@/types/chat'
import {
  EStepNames,
  EStepStatus,
} from '@/types/chat'
import { markdown } from '@/utils/common'

interface IProps {
  steps?: IStep[]
  isPendingResponse: boolean
}

const props = withDefaults(defineProps<IProps>(), {
  steps: () => [],
  isPendingResponse: false,
})

const { t } = useI18n()

const latestStep = ref()

const getStepName = (step: IStep) => {
  const stepNames = new Map([
    [EStepNames.QUESTION_AGENT, t('chat.questionAgent')],
    [EStepNames.SQL_GENERATOR_AGENT, t('chat.sqlGeneratorAgent')],
    [EStepNames.DB_QUERY_AGENT, t('chat.dbQueryAgent')],
    [EStepNames.ANSWER_GENERATOR_AGENT, t('chat.displayAgent')],
  ])
  return stepNames.get(step.step) || t('common.query')
}

const getNewQuestion = (step: IStep) => {
  if (step.step !== EStepNames.QUESTION_AGENT) {
    return ''
  }
  const result: Record<string, any> = step.result ?? { newQuestion: '' }
  return result?.newQuestion
}

watch(() => props.steps, (value) => {
  if (value.length) {
    latestStep.value = value[value.length - 1]
  }
}, { deep: true, immediate: true })
</script>

<template>
  <template v-if="steps.length">
    <div
      v-if="isPendingResponse"
      class="w-fit mb-4 px-5 py-2 border rounded-[12px]"
    >
      <div
        v-for="step in steps"
        :key="step.step + step.status"
        class="flex justify-between items-center py-[3px]"
      >
        <div class="flex items-center">
          <StepStatus :step="step" />
          <span class="text-sm text-text-2">
            {{ getStepName(step) }}
          </span>
        </div>
        <div
          v-if="step.status !== EStepStatus.IN_PROGRESS"
          class="ml-10"
        >
          <span class="ml-3 text-[12px] text-text-2">
            {{ t('chat.latency') }}
          </span>
          <span class="ml-1 text-[12px] text-text-2">
            {{ step.latency }}s
          </span>
        </div>
      </div>
    </div>
    <a-collapse
      v-else
      class="relative left-[-16px]"
      :bordered="false"
      style="background: rgb(255, 255, 255)"
    >
      <template #expandIcon="{ isActive }">
        <div class="w-fit mb-4 px-3 py-2 border rounded-[12px]">
          <CaretRightOutlined
            class="mr-2 text-text-4 text-xs"
            :rotate="isActive ? 90 : 0"
          />
          <StepStatus :step="latestStep" />
          <span class="text-sm text-text-2 font-medium">{{ getStepName(latestStep) }}</span>
        </div>
      </template>
      <a-collapse-panel>
        <template #header>
          <span />
        </template>
        <div class="w-fit mb-4 px-5 py-2 border rounded-[12px]">
          <div
            v-for="step in steps"
            :key="step.step + step.status"
            class="flex flex-col py-[3px]"
          >
            <div class="flex justify-between items-center">
              <div class="flex items-center">
                <StepStatus :step="step" />
                <span class="text-sm text-text-2">
                  {{ getStepName(step) }}
                </span>
              </div>
              <div
                v-if="step.status !== EStepStatus.IN_PROGRESS"
                class="ml-10"
              >
                <span class="ml-3 text-[12px] text-text-2">
                  {{ t('chat.latency') }}
                </span>
                <span class="ml-1 text-[12px] text-text-2">
                  {{ step.latency }}s
                </span>
              </div>
            </div>
            <div
              v-if="getNewQuestion(step)"
              class="mt-2"
            >
              <a-collapse :bordered="false">
                <a-collapse-panel>
                  <template #header>
                    <span class="text-xs text-text-3">{{ t('chat.optimizedQuestion') }}</span>
                  </template>
                  <div
                    class="text-sm text-text-1"
                    v-html="markdown.render(getNewQuestion(step))"
                  />
                </a-collapse-panel>
              </a-collapse>
            </div>
            <div
              v-if="step.step === EStepNames.SQL_GENERATOR_AGENT && Array.isArray(step.result) && step.result.length"
              class="mt-2"
            >
              <a-collapse :bordered="false">
                <a-collapse-panel>
                  <template #header>
                    <span class="text-xs text-text-3">{{ t('chat.sqlPreview') }}</span>
                  </template>
                  <div v-html="markdown.render(`\`\`\`sql\n${step.result[0]}\n\`\`\``)" />
                </a-collapse-panel>
              </a-collapse>
            </div>
            <div
              v-if="step.step === EStepNames.DB_QUERY_AGENT && step.status === EStepStatus.ERROR && step.result"
              class="mt-2"
            >
              <a-collapse :bordered="false">
                <a-collapse-panel>
                  <template #header>
                    <span class="text-xs text-text-3">{{ t('chat.errorMessage') }}</span>
                  </template>
                  <div v-html="markdown.render(`\`\`\`\n${step.result}\n\`\`\``)" />
                </a-collapse-panel>
              </a-collapse>
            </div>
          </div>
        </div>
      </a-collapse-panel>
    </a-collapse>
  </template>
</template>

<style scoped lang="scss">
:deep(.ant-collapse) {
  .ant-collapse-content {
    background-color: transparent;

    strong {
      display: inline-block;
      padding: 0 3px;
      font-weight: 500;
    }
  }

  .ant-collapse-arrow {
    font-size: 12px !important;
    color: #9898A3 !important;
  }
}

:deep(code.hljs.language-sql) {
  max-width: 500px;
  white-space: normal;
  overflow-x: hidden;
  padding: 20px !important;
}

:deep(code.hljs) {
  max-width: 500px;
  white-space: normal;
  overflow-x: hidden;
  padding: 20px !important;
}
</style>
