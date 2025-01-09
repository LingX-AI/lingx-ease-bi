<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  ClearOutlined,
  CloudDownloadOutlined,
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  UploadOutlined,
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import QuestionCard from './QuestionCard.vue'
import PromptModal from './PromptModal.vue'
import { markdown } from '@/utils/common'

const { applicationId } = defineProps<IProps>()

const { t } = useI18n()

interface IProps {
  applicationId: string | number
}

const {
  questions,
  pagination,
  getFineTuningExamples,
  fineTuningExamples,
  loadingFineTuningExample,
  loadingExportFineTuningExample,
  createFineTuningQuestions,
  deleteFineTuningExample,
  exportFineTuningExample,
  loadingCreateFineTuningQuestions,
} = useFineTuningExample(applicationId)

const questionCount = ref(10)
const questionCountList = [10, 20, 50, 100]
const showPromptModal = ref(false)
const selectedRowKeys = ref<string[]>([])
const fineTuningExampleColumns = computed(() => [
  {
    title: t('dataset.fineTuningExample.title'),
    dataIndex: 'question',
    width: 320,
  },
  {
    title: 'SQL',
    dataIndex: 'sql',
  },
  {
    title: t('common.createTime'),
    dataIndex: 'createdAt',
    width: 160,
  },
  {
    title: t('common.actions'),
    align: 'center',
    dataIndex: 'action',
    width: 100,
    fixed: 'right',
  },
])
getFineTuningExamples({
  application: applicationId,
})

const _createFineTuningQuestions = () => {
  createFineTuningQuestions({
    applicationId,
    questionCount: questionCount.value,
  })
}

const editPrompt = () => {
  showPromptModal.value = true
}

const onSelectChange = (_selectedRowKeys: string[]) => {
  selectedRowKeys.value = _selectedRowKeys
}

const handleImportJson = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target?.result as string)
      questions.value = [...questions.value, ...json]
    }
    // eslint-disable-next-line unused-imports/no-unused-vars
    catch (_) {
      message.error(t('dataset.fineTuningExample.importError'))
    }
  }
  reader.readAsText(file)
  return false
}

const showImportModal = ref(false)
const importFileList = ref<any[]>([])
const pastedJson = ref('')

const handleImport = () => {
  showImportModal.value = true
}

const handleImportModalOk = () => {
  if (importFileList.value.length === 0 && !pastedJson.value) {
    message.warning(t('dataset.fineTuningExample.importFileRequired'))
    return
  }

  if (importFileList.value.length > 0) {
    const file = importFileList.value[0].originFileObj
    handleImportJson(file)
  }
  else if (pastedJson.value) {
    handlePasteJson()
  }

  showImportModal.value = false
  importFileList.value = []
  pastedJson.value = ''
}

const handleImportModalCancel = () => {
  showImportModal.value = false
  importFileList.value = []
  pastedJson.value = ''
}

const beforeUpload = (file: File) => {
  const isJSON = file.type === 'application/json'
  if (!isJSON) {
    message.error(t('dataset.fineTuningExample.importFormatError'))
  }
  return false
}

const handlePasteJson = () => {
  try {
    const json = JSON.parse(pastedJson.value)
    if (!Array.isArray(json)) {
      throw new TypeError('Not an array')
    }
    questions.value = [...questions.value, ...json]
    showImportModal.value = false
    pastedJson.value = ''
  }
  // eslint-disable-next-line unused-imports/no-unused-vars
  catch (_) {
    message.error(t('dataset.fineTuningExample.importError'))
  }
}

const handleAddQuestion = () => {
  questions.value.push({
    question: '',
    sql: '',
    createdAt: new Date().toISOString(),
  })
}
</script>

<template>
  <div class="w-full h-full flex">
    <div class="flex flex-col flex-shrink-0 w-[560px] h-full mr-5 border rounded-[10px] overflow-hidden">
      <div class="flex justify-between items-center mb-5 p-5 pb-0">
        <span class="text-sm font-medium">
          <span>{{ t('dataset.fineTuningExample.title') }}</span>
          <span class="ml-1 text-text-3 font-normal">({{ questions.length }})</span>
        </span>
        <div class="flex-center">
          <a-button
            class="mr-2"
            type="primary"
            size="small"
            :loading="loadingCreateFineTuningQuestions"
            @click="_createFineTuningQuestions"
          >
            <span class="text-xs">{{ t('dataset.fineTuningExample.generateQuestions') }}</span>
          </a-button>
          <a-select
            v-model:value="questionCount"
            size="small"
            style="width: 120px"
            class="mr-2"
          >
            <a-select-option
              v-for="item in questionCountList"
              :key="item"
              size="small"
              :value="item"
            >
              <span class="text-xs">{{ item }} {{ t('dataset.fineTuningExample.count') }}</span>
            </a-select-option>
          </a-select>
          <a-dropdown>
            <a-button size="small">
              <span class="text-xs flex items-center">
                {{ t('common.more') }}
              </span>
            </a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="editPrompt">
                  <span class="text-xs flex items-center">
                    <EditOutlined class="mr-1" />
                    {{ t('dataset.fineTuningExample.prompt') }}
                  </span>
                </a-menu-item>
                <a-menu-item @click="handleAddQuestion">
                  <span class="text-xs flex items-center">
                    <PlusOutlined class="mr-1" />
                    {{ t('dataset.fineTuningExample.addQuestion') }}
                  </span>
                </a-menu-item>
                <a-menu-item @click="handleImport">
                  <span class="text-xs flex items-center">
                    <UploadOutlined class="mr-1" />
                    {{ t('dataset.fineTuningExample.importQuestions') }}
                  </span>
                </a-menu-item>
                <a-menu-item @click="questions = []">
                  <span class="text-xs flex items-center">
                    <ClearOutlined class="mr-1" />
                    {{ t('dataset.fineTuningExample.clearQuestions') }}
                  </span>
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </div>
      <div class="flex-1 p-5 overflow-y-auto">
        <QuestionCard
          v-for="question in questions"
          :key="question.question"
          :question="question.question"
          :sql="question.sql"
          :application-id="applicationId"
          @refresh-data="getFineTuningExamples({ application: applicationId })"
          @delete="questions = questions.filter((item) => item.question !== question.question)"
        />
        <no-data
          v-if="!questions.length"
          class="relative top-[300px]"
        />
      </div>
    </div>
    <div class="flex-1">
      <div class="flex justify-between mb-3">
        <span class="text-sm font-medium">
          <span>{{ t('dataset.fineTuningExample.fineTuningExamples') }}</span>
          <span class="ml-1 text-text-3 font-normal">({{ pagination.total }})</span>
        </span>
        <div class="flex">
          <a-dropdown>
            <a-button
              class="flex-center mr-2"
              type="primary"
              size="small"
              :loading="loadingExportFineTuningExample"
            >
              <CloudDownloadOutlined />
              <span>{{ t('dataset.fineTuningExample.export') }}</span>
            </a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="exportFineTuningExample(applicationId, 'json')">
                  {{ t('dataset.fineTuningExample.exportJson') }}
                </a-menu-item>
                <a-menu-item @click="exportFineTuningExample(applicationId, 'csv')">
                  {{ t('dataset.fineTuningExample.exportCsv') }}
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
          <a-button
            class="flex-center"
            type="primary"
            size="small"
            danger
            @click="deleteFineTuningExample(selectedRowKeys)"
          >
            <DeleteOutlined />
            <span>{{ t('common.delete') }}</span>
          </a-button>
        </div>
      </div>
      <a-table
        row-key="id"
        bordered
        :row-selection="{ selectedRowKeys, onChange: onSelectChange }"
        :loading="loadingFineTuningExample"
        :dataSource="fineTuningExamples"
        :columns="fineTuningExampleColumns"
        :scroll="{ y: 'calc(100vh - 240px)', x: 100 }"
        :pagination="pagination"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'sql'">
            <a-tooltip color="#FFFFFF">
              <template #title>
                <div
                  class="text-text-2"
                  v-html="markdown.render(record.sql)"
                />
              </template>
              <span class="line-clamp-1">{{ record.sql }}</span>
            </a-tooltip>
          </template>
          <template v-if="column.dataIndex === 'action'">
            <a-button
              type="text"
              size="small"
              @click="deleteFineTuningExample([record.id])"
            >
              <div class="flex-center">
                <DeleteOutlined />
              </div>
            </a-button>
          </template>
        </template>
      </a-table>
    </div>
  </div>
  <PromptModal
    v-if="showPromptModal"
    :application-id="applicationId"
    prompt-field-name="questionBuilderPrompt"
    :afterClose="() => showPromptModal = false"
  />
  <a-modal
    v-model:visible="showImportModal"
    width="600px"
    :title="t('dataset.fineTuningExample.importQuestions')"
    :okText="t('common.confirm')"
    :cancelText="t('common.cancel')"
    @ok="handleImportModalOk"
    @cancel="handleImportModalCancel"
  >
    <div class="mb-4">
      <div class="p-4 bg-gray-50 rounded-lg mb-4 text-sm">
        <div class="font-medium mb-2">
          {{ t('dataset.fineTuningExample.importTip.title') }}
        </div>
        <ul class="list-disc pl-5 text-gray-600">
          <li>{{ t('dataset.fineTuningExample.importTip.format') }}</li>
          <li class="font-mono text-xs mt-2">
            [{ "question": "", "sql": "" }, { "question": "", "sql": "" }]
          </li>
        </ul>
      </div>
      <a-upload-dragger
        v-model:fileList="importFileList"
        :maxCount="1"
        accept=".json"
        :beforeUpload="beforeUpload"
        :showUploadList="{ showRemoveIcon: true }"
        :customRequest="() => { }"
      >
        <p class="ant-upload-drag-icon">
          <UploadOutlined />
        </p>
        <p class="text-sm text-text-2">
          {{ t('dataset.fineTuningExample.importTip.dragText') }}
        </p>
      </a-upload-dragger>
    </div>
    <div class="mt-4">
      <div class="text-sm font-medium mb-2">
        {{ t('dataset.fineTuningExample.importTip.pasteTitle') }}
      </div>
      <a-textarea
        v-model:value="pastedJson"
        :placeholder="t('dataset.fineTuningExample.importTip.pastePlaceholder')"
        :rows="10"
      />
    </div>
  </a-modal>
</template>

<style scoped lang="scss">
:deep(td.ant-table-cell) {
  padding: 4px 8px !important;
  font-size: 13px !important;
}

:deep(th.ant-table-cell) {
  font-size: 13px !important;
}
</style>
