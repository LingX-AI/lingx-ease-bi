<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { InfoCircleOutlined } from '@ant-design/icons-vue'
import { usePrompt } from '@/composables/specific/app'
import type { IAppPrompt } from '@/types/app'

interface IProps {
  applicationId: string | number
  promptFieldName?: 'questionCleanPrompt' | 'columnCommentPrompt' | 'questionBuilderPrompt' | 'sqlGeneratorPrompt' | 'schemaRagPrompt'
  showAllPrompt?: boolean
}

const { applicationId, promptFieldName, showAllPrompt = false } = defineProps<IProps>()
const open = ref(false)
const { t } = useI18n()
const { appPrompt, getAppPrompt, updateAppPrompt } = usePrompt()

getAppPrompt(applicationId)
const curSegmented = ref<NonNullable<IProps['promptFieldName']>>(promptFieldName || 'questionCleanPrompt')

const title = computed(() => {
  if (showAllPrompt) {
    return t('common.promptWord')
  }
  switch (curSegmented.value) {
    case 'questionCleanPrompt':
      return t('dataset.promptWord.questionClean')
    case 'columnCommentPrompt':
      return t('dataset.promptWord.columnComment')
    case 'questionBuilderPrompt':
      return t('dataset.promptWord.questionBuilder')
    case 'sqlGeneratorPrompt':
      return t('dataset.promptWord.sqlGenerator')
    case 'schemaRagPrompt':
      return t('dataset.promptWord.schemaRagPrompt')
    default:
      return t('common.promptWord')
  }
})

const segmentedOptions = [
  { label: t('dataset.promptWord.questionClean'), value: 'questionCleanPrompt' },
  { label: t('dataset.promptWord.columnComment'), value: 'columnCommentPrompt' },
  { label: t('dataset.promptWord.questionBuilder'), value: 'questionBuilderPrompt' },
  { label: t('dataset.promptWord.schemaRagPrompt'), value: 'schemaRagPrompt' },
  { label: t('dataset.promptWord.sqlGenerator'), value: 'sqlGeneratorPrompt' },
]

const promptVariables = {
  questionCleanPrompt: ['{application_name}', '{application_description}'],
  columnCommentPrompt: ['{application_description}', '{database_tables}'],
  questionBuilderPrompt: ['{application_description}', '{database_schema}'],
  sqlGeneratorPrompt: ['{db}', '{database_schema}'],
  schemaRagPrompt: ['{database_schema}'],
}

const handleOk = () => {
  const _appPrompt: IAppPrompt = { applicationId: appPrompt.applicationId }
  _appPrompt[curSegmented.value] = appPrompt[curSegmented.value]
  updateAppPrompt(_appPrompt)
  if (!showAllPrompt) {
    open.value = false
  }
}
onMounted(() => {
  open.value = true
})
</script>

<template>
  <a-modal
    v-model:open="open"
    :title="title"
    centered
    :width="showAllPrompt ? '1000px' : '700px'"
    :ok-text="t('common.save')"
    v-bind="$attrs"
    @ok="handleOk"
  >
    <div class="p-5 pt-2">
      <div
        v-if="showAllPrompt"
        class="flex-center"
      >
        <a-segmented
          v-model:value="curSegmented"
          class="mx-auto mb-3"
          :options="segmentedOptions"
        />
      </div>
      <div class="mb-3 bg-bg-2 rounded p-2 text-[13px]">
        <InfoCircleOutlined class="mr-1 text-text-2" />
        <span class="text-text-2">{{ t('dataset.promptWord.variableTip', { promptVariables: promptVariables[curSegmented].join(', ') }) }}</span>
        <span class="text-text-2">{{ t('dataset.promptWord.bracketsTip') }}</span>
      </div>
      <a-textarea
        v-model:value="appPrompt[curSegmented]"
        :placeholder="t('dataset.promptWord.placeholder')"
        :auto-size="{ minRows: 25, maxRows: 25 }"
      />
    </div>
  </a-modal>
</template>

<style scoped lang="scss"></style>
