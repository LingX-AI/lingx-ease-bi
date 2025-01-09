<script setup lang="ts">
import { LeftOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import { useEmbedding } from '@/composables/specific/app'
import { markdown } from '@/utils/common'

interface IProps {
  applicationId: string | number
}

const { applicationId } = defineProps<IProps>()
const { t } = useI18n()

const searchContent = ref('')
const showRetrievalDocument = inject('showRetrievalDocument', ref(false))

const {
  retrievedDocuments,
  retrievalAppDatabaseDocument,
} = useEmbedding()

const handleRetrieval = (applicationId: string | number, searchContent: string) => {
  if (!searchContent.trim()) {
    retrievedDocuments.value = []
    return
  }
  retrievalAppDatabaseDocument(applicationId, searchContent)
}

const getMarkdownCodeStr = (content: string) => {
  return markdown.render(`\`\`\`json
  ${content}
  \`\`\``)
}
</script>

<template>
  <div>
    <div class="flex items-center">
      <a-button
        type="text"
        size="small"
        class="flex-center mr-2"
        @click="showRetrievalDocument = false"
      >
        <LeftOutlined />
        <span>{{ t('common.back') }}</span>
      </a-button>
      <span class="text-sm font-medium">{{ t('dataset.retrievalDocument') }}</span>
    </div>
    <div class="flex flex-col items-center w-full mt-5 h-full">
      <div class="flex-shrink-0">
        <a-input-search
          v-model:value="searchContent"
          class="w-[600px]"
          :placeholder="t('dataset.enterRetrievalContent')"
          @search="handleRetrieval(applicationId, searchContent)"
        />
      </div>
      <div class="flex-1 mt-5 pb-5 px-10 overflow-y-auto">
        <template v-if="retrievedDocuments.length">
          <div
            v-for="(item, index) in retrievedDocuments"
            :key="index"
            class="w-full mb-3 p-5 rounded-[10px] text-sm bg-bg-2 whitespace-normal break-words overflow-hidden"
          >
            <div
              class="h-[200px] overflow-y-auto"
              v-html="getMarkdownCodeStr(item.content)"
            />
            <div class="py-2 text-xs text-text-2">
              <span>{{ t('dataset.similarity') }}：</span>
              <span>{{ item.similarity }}</span>
            </div>
          </div>
        </template>
        <template v-else>
          <no-data class="relative top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        </template>
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
