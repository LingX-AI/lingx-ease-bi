<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useFineTuningExample } from '@/composables/specific/app'
import { markdown } from '@/utils/common'
import PromptModal from '@/views/AIDataset/components/PromptModal.vue'
import { useCopy } from '@/composables/common'
import NoData from '@/components/common/NoData.vue'

interface IProps {
  applicationId: string | number
}

const { applicationId } = defineProps<IProps>()
const { t } = useI18n()
const hasStandardFineTuningExamples = ref(false)
const showPromptModal = ref(false)
const {
  fineTuningConfig,
  standardFineTuningExamples,
  getFineTuningConfig,
  getStandardFineTuningExample,
  openFineTuningWebUI,
} = useFineTuningExample()

const { handleCopy } = useCopy()

const standardFineTuningExamplesMarkdown = computed(() => {
  return markdown.render(`\`\`\`json
  ${JSON.stringify(standardFineTuningExamples.value, null, 4)}
  \`\`\``)
})

const fineTuningConfigMarkdown = computed(() => {
  if (!fineTuningConfig.value)
    return ''
  return markdown.render(`\`\`\`yaml
  ${fineTuningConfig.value.config}
  \`\`\``)
})

const handleOpenWebUI = async () => {
  const { webuiUrl } = await openFineTuningWebUI()
  if (webuiUrl) {
    window.open(webuiUrl, '_blank')
  }
}

const handleDownloadTrainingData = () => {
  const jsonString = JSON.stringify(standardFineTuningExamples.value, null, 2)
  const blob = new Blob([jsonString], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'training_data.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const handleDownloadConfig = () => {
  if (!fineTuningConfig.value?.config)
    return
  const blob = new Blob([fineTuningConfig.value.config], { type: 'text/yaml' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'training_config.yaml'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  getFineTuningConfig(applicationId)
  getStandardFineTuningExample(applicationId).then(() => {
    hasStandardFineTuningExamples.value = standardFineTuningExamples.value.length > 0
  })
})
</script>

<template>
  <div class="w-full h-full flex">
    <div class="flex flex-col flex-1 h-full mr-5 p-5 border rounded-[10px] overflow-hidden">
      <div class="flex justify-between items-center mb-5 pb-0">
        <span class="flex-center text-sm font-medium">
          <span>{{ t('dataset.fineTuningModel.trainingData') }}</span>
          <span class="ml-2 text-text-2 text-xs font-normal">{{ standardFineTuningExamples.length }}</span>
        </span>
        <span>
          <a-button
            class="mr-2"
            size="small"
            @click="handleCopy(JSON.stringify(standardFineTuningExamples))"
          >
            {{ t('dataset.fineTuningModel.copy') }}
          </a-button>
          <a-button
            class="mr-2"
            size="small"
            @click="showPromptModal = true"
          >
            {{ t('dataset.fineTuningModel.prompt') }}
          </a-button>
          <a-button
            type="primary"
            size="small"
            @click="handleDownloadTrainingData"
          >
            {{ t('dataset.fineTuningModel.download') }}
          </a-button>
        </span>
      </div>
      <div
        v-if="standardFineTuningExamples.length"
        class="p-3 text-sm overflow-x-hidden whitespace-normal break-words"
        v-html="standardFineTuningExamplesMarkdown"
      />
      <NoData
        v-else
        class="relative top-[30vh]"
      />
    </div>
    <div class="flex flex-col flex-1 w-[560px] h-full mr-5 p-5 border rounded-[10px] overflow-hidden">
      <div class="flex justify-between items-center mb-5 pb-0">
        <span class="flex justify-between items-center text-sm font-medium">
          <span>{{ t('dataset.fineTuningModel.trainingParameters') }}</span>
          <span class="ml-2 text-xs text-text-2 font-normal">
            <span>{{ t('dataset.fineTuningModel.parameterNote') }}</span>
            <a
              href="https://github.com/hiyouga/LLaMA-Factory/tree/main"
              class="underline text-primary"
              target="_blank"
            >LLaMA-Factory</a>
          </span>
        </span>
        <span>
          <a-button
            class="mr-2"
            size="small"
            @click="handleCopy(fineTuningConfig.config)"
          >
            {{ t('dataset.fineTuningModel.copy') }}
          </a-button>
          <a-button
            class="mr-2"
            size="small"
            @click="handleDownloadConfig"
          >
            {{ t('dataset.fineTuningModel.download') }}
          </a-button>
          <a-button
            type="primary"
            size="small"
            @click="handleOpenWebUI"
          >
            {{ t('dataset.fineTuningModel.startFineTuning') }}
          </a-button>
        </span>
      </div>
      <div
        class="p-3 text-sm overflow-x-hidden whitespace-normal"
        v-html="fineTuningConfigMarkdown"
      />
    </div>
  </div>
  <PromptModal
    v-if="showPromptModal"
    :application-id="applicationId"
    prompt-field-name="sqlGeneratorPrompt"
    :afterClose="() => showPromptModal = false"
  />
</template>

<style scoped lang="scss">
:deep(code.hljs) {
  text-indent: -1rem;
  white-space: pre-wrap;
  overflow-x: hidden;
}
</style>
