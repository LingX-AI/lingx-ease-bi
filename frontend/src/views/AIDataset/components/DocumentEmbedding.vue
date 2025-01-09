<script setup lang="ts">
import { RightCircleOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import { useDataStructure, useEmbedding } from '@/composables/specific/app'

interface IProps {
  applicationId: string | number
}

const { applicationId } = defineProps<IProps>()
const { t } = useI18n()
const {
  getAppDatabaseSchema,
} = useDataStructure()
const {
  databaseDocuments,
  loadingRetrievalAppDatabaseDocument,
  getAppDatabaseDocument,
  createAppDatabaseDocument,
  loadingCreateAppDatabaseDocument,
} = useEmbedding()

const showRetrievalDocument = inject('showRetrievalDocument', ref(false))

const columns = [
  {
    title: t('dataset.documentName'),
    dataIndex: 'documentName',
    width: 160,
    fixed: 'left',
  },
  {
    title: t('dataset.type'),
    dataIndex: 'contentType',
    width: 80,
  },
  {
    title: t('dataset.size'),
    dataIndex: 'documentSize',
    width: 120,
  },
  {
    title: t('dataset.tokenCount'),
    dataIndex: 'tokenCount',
    width: 120,
  },
  {
    title: t('dataset.characterCount'),
    dataIndex: 'characterCount',
    width: 100,
  },
]

getAppDatabaseSchema(applicationId)
getAppDatabaseDocument(applicationId)
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex items-center justify-between flex-shrink-0 mb-5">
      <div class="flex-center">
        <span class="text-sm font-medium">{{ t('dataset.embeddingDocument.title') }}</span>
        <span v-if="databaseDocuments.length" class="ml-2 text-sm text-text-3">{{ databaseDocuments.length }}</span>
        <span class="ml-2 text-xs text-text-2 font-normal">{{ t('dataset.embeddingDocument.notRecommended') }}</span>
      </div>
      <div
        v-if="databaseDocuments.length"
        class="flex"
      >
        <a-button
          type="primary"
          size="small"
          class="flex-center mr-2"
          :loading="loadingCreateAppDatabaseDocument"
          @click="createAppDatabaseDocument(applicationId)"
        >
          <RightCircleOutlined />
          {{ t('chat.regenerate') }}
        </a-button>
        <a-button
          type="primary"
          size="small"
          class="flex-center"
          @click="showRetrievalDocument = true"
        >
          <RightCircleOutlined />
          {{ t('dataset.tryItOut') }}
        </a-button>
      </div>
    </div>
    <div class="flex-1 pr-2 overflow-y-auto">
      <a-table
        v-if="databaseDocuments.length"
        rowKey="name"
        bordered
        :dataSource="databaseDocuments"
        :columns="columns"
        :pagination="false"
        size="small"
        :loading="loadingRetrievalAppDatabaseDocument"
        :scroll="{ y: 'calc(100vh - 203px)', x: 100 }"
      />
      <div
        v-else-if="!loadingRetrievalAppDatabaseDocument"
        class="flex-center flex-col h-full"
      >
        <NoData :text="t('dataset.noEmbeddingDocuments')" />
        <a-button
          type="primary"
          class="w-[300px]"
          :loading="loadingCreateAppDatabaseDocument"
          @click="createAppDatabaseDocument(applicationId)"
        >
          {{ t('dataset.createNow') }}
        </a-button>
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
