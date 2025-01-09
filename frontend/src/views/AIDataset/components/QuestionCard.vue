<script setup lang="ts">
import {
  CloudUploadOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons-vue'
import type { TableColumn } from 'ant-design-vue'
import { onClickOutside } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { markdown } from '@/utils/common'
import { useFineTuningExample } from '@/composables/specific/app'

interface IProps {
  applicationId: string | number
  sql?: string
  question?: string
}

const { applicationId, question: _question, sql: _sql } = defineProps<IProps>()
const emit = defineEmits(['delete', 'refresh-data'])
const question = ref(_question)
const sql = ref(_sql)
const spinning = ref(false)
const executionResult = ref([])
const executionResultCols = ref<typeof TableColumn[]>([])
const duration = ref(0)
const executionError = ref('')
const hasBenExecuted = ref(false)
const idEditSql = ref(false)
const sqlMarkdownBoxRef = ref(null)
const _sqlMarkdown = computed(() => {
  return markdown.render(`\`\`\`sql
  ${sql.value}
  \`\`\``)
})

const {
  loadingCreateSql,
  loadingExecuteSql,
  createSql,
  executeSql,
  saveSql,
} = useFineTuningExample()

const handleGenerateSql = async () => {
  const _sql = await createSql({ applicationId, question: question.value! })
  if (_sql) {
    sql.value = _sql
  }
}

onClickOutside(sqlMarkdownBoxRef, () => {
  idEditSql.value = false
})

const handleExecuteSql = async () => {
  hasBenExecuted.value = false
  const { result, error, duration: _duration } = await executeSql({
    applicationId,
    question: question.value!,
    sql: sql.value!,
  })
    .finally(() => {
      hasBenExecuted.value = true
    })
  duration.value = _duration || 0
  if (error) {
    question.value = error
    executionError.value = t('dataset.fineTuningExample.executionError')
    executionResult.value = []
    return
  }
  executionError.value = ''
  executionResult.value = result
  if (result?.length) {
    executionResultCols.value = Object.keys(result[0]).map((item) => {
      return {
        title: item,
        dataIndex: item,
        width: 150,
      } as any
    })
  }
}

const handleSaveSql = async () => {
  const data = await saveSql({ application: applicationId, question: question.value!, sql: sql.value! })
  if (data) {
    emit('refresh-data')
    emit('delete')
  }
}

const { t } = useI18n()
</script>

<template>
  <a-spin :spinning="spinning">
    <div class="flex flex-col border rounded-[5px] mb-5">
      <a-textarea
        v-model:value="question"
        :bordered="false"
        class="p-3 text-sm bg-bg-1/5 rounded-0 hover:bg-bg-1/5"
        :placeholder="t('dataset.fineTuningExample.enterQuestion')"
        auto-size
      />
      <a-spin
        :spinning="loadingCreateSql"
        size="small"
      >
        <a-textarea
          v-if="idEditSql"
          ref="sqlMarkdownBoxRef"
          v-model:value="sql"
          :bordered="false"
          autosize
          class="p-3 text-sm "
        />
        <div
          v-else
          class="p-3 text-sm overflow-x-hidden whitespace-normal"
          @click="idEditSql = true"
          v-html="_sqlMarkdown"
        />
      </a-spin>
      <a-spin
        v-if="sql"
        :spinning="loadingExecuteSql"
        size="small"
      >
        <div
          v-if="hasBenExecuted"
          class="flex flex-col"
        >
          <div class="p-2 border-t">
            <span>{{ t('dataset.fineTuningExample.executionResult') }}</span>
            <span class="ml-2 text-text-3 text-xs">
              <span>{{ duration }}s</span>
              <template v-if="executionError">
                <span class="mx-2">|</span>
                <span class="text-warning">{{ executionError }}</span>
              </template>
              <template v-else>
                <span class="mx-2">|</span>
                <span class="text-success">{{ t('dataset.fineTuningExample.executionSuccess') }}</span>
                <template v-if="executionResult.length === 0">
                  <span class="mx-2">|</span>
                  <span class="text-success">{{ t('dataset.fineTuningExample.noResult') }}</span>
                </template>
              </template>
            </span>
          </div>
          <a-table
            v-if="executionResult.length"
            :dataSource="executionResult"
            :columns="executionResultCols"
            :scroll="{ y: 300 }"
          />
        </div>
      </a-spin>
      <div class="flex justify-end p-3 text-sm bg-bg-1/5 text-text-2">
        <ReloadOutlined
          class="text-[16px] mr-4 cursor-pointer"
          @click="handleGenerateSql"
        />
        <PlayCircleOutlined
          class="text-[16px] mr-4 cursor-pointer"
          @click="handleExecuteSql"
        />
        <CloudUploadOutlined
          v-if="sql"
          class="text-[18px] mr-4 cursor-pointer"
          @click="handleSaveSql"
        />
        <DeleteOutlined
          class="text-[18px] cursor-pointer"
          @click="$emit('delete')"
        />
      </div>
    </div>
  </a-spin>
</template>

<style scoped lang="scss">
:deep(code.hljs.language-sql) {
  white-space: normal;
  overflow-x: hidden;
}
</style>
