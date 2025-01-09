<script setup lang="ts">
import { DownOutlined, QuestionCircleOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import { useAppDatabase, useDataStructure } from '@/composables/specific/app'
import { markdown } from '@/utils/common'

interface IProps {
  applicationId: string | number
}

const { applicationId } = defineProps<IProps>()
const { t } = useI18n()
const { enableDisableRag, getApplication } = useAppDatabase()
const { appDatabaseSchema, getAppDatabaseSchema } = useDataStructure()

const enableRAG = ref(false)

getAppDatabaseSchema(applicationId)
getApplication(applicationId).then((data) => {
  enableRAG.value = data.agentConfiguration?.ragEnabled ?? true
})
const expandedIndex = ref()
const getMarkdownCodeStr = (appDatabaseSchema: Record<string, any>) => {
  return markdown.render(`\`\`\`json
  ${JSON.stringify(appDatabaseSchema)}
  \`\`\``)
}

const handleEnableDisableRag = (isEnabled: boolean) => {
  enableDisableRag(applicationId, isEnabled)
}
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex items-center justify-between w-full flex-shrink-0 mb-5">
      <div class="flex items-center">
        <span class="text-sm font-medium">{{ t('dataset.databaseTableDocument') }}</span>
        <span class="ml-2 text-sm text-text-3">{{ appDatabaseSchema.length }}</span>
      </div>
      <div class="flex items-center mr-2">
        <a-switch
          v-model:checked="enableRAG"
          class="ml-2"
          size="small"
          @change="handleEnableDisableRag"
        />
        <span class="ml-2 text-xs text-text-2 font-normal">
          {{ t('dataset.enableRetrieval') }}
          <a-popover>
            <template #content>
              <div class="w-[300px] text-xs text-text-2 font-normal">
                <p>{{ t('dataset.retrievalTip.line1') }}</p>
                <p>{{ t('dataset.retrievalTip.line2') }}</p>
              </div>
            </template>
            <QuestionCircleOutlined />
          </a-popover>
        </span>
      </div>
    </div>
    <div class="flex-1 w-[500px] pr-2 overflow-y-auto">
      <div
        v-for="(item, index) in appDatabaseSchema"
        :key="item.table"
        class="text-sm border rounded-[10px] mb-2 overflow-hidden cursor-pointer"
        @click="expandedIndex === index ? expandedIndex = null : expandedIndex = index"
      >
        <div class="flex justify-between px-3 py-1 text-xs font-bold bg-bg-2">
          <span class="text-text-2"># {{ index + 1 }}</span>
          <div>
            <span class="text-xs text-text-3 font-normal mr-2">{{
              JSON.stringify(item).length
            }} {{ t('dataset.characters') }}</span>
            <DownOutlined
              class="text-text-2 transition"
              :class="expandedIndex === index ? 'rotate-180' : ''"
            />
          </div>
        </div>
        <div
          class="px-2 pb-2 text-sm"
          :class="expandedIndex === index ? 'h-fit' : 'h-[100px]'"
          v-html="getMarkdownCodeStr(item)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
:deep(code.hljs.language-json) {
  white-space: normal;
  word-break: break-word;
  overflow-x: hidden;
}
</style>
