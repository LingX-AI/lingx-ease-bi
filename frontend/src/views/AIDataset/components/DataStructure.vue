<script setup lang="ts">
import {
  CheckOutlined,
  CloudDownloadOutlined,
  CloudSyncOutlined,
  EditOutlined,
  RightCircleOutlined,
  SaveOutlined,
  TableOutlined,
} from '@ant-design/icons-vue'
import { Modal, message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import type { IAppTable, ITableColumn } from '@/types/app'
import PromptModal from '@/views/AIDataset/components/PromptModal.vue'

const { applicationId } = defineProps<IProps>()

const { t } = useI18n()

interface IProps {
  applicationId: string | number
}

const currentTable = ref<IAppTable>()
const showEditAppTables = ref(false)
// 自动替换最终的AI注释
const autoReplace = ref(true)
const showPromptModal = ref(false)

const {
  dataStructureTree,
  tableColumns,
  getDataStructure,
  getAppTableColumns,
  createDataStructure,
  loadingGetTableColumns,
  updateAppTable,
  updateAppTableColumn,
  batchUpdateAppTableColumn,
  loadingGetDataStructure,
  loadingCreateDataStructure,
  loadingGetAppTableAIComment,
  getAppTableAIComment,
  exportAppDatabaseSchema,
} = useDataStructure()

const handleGetDataStructure = async () => {
  await getDataStructure(applicationId as number)
  if (dataStructureTree.value.length) {
    currentTable.value = dataStructureTree.value[0]
    getAppTableColumns(currentTable.value.id)
  }
}

handleGetDataStructure()

const columns = computed(() => [
  {
    title: t('dataset.fieldName'),
    dataIndex: 'name',
    width: 160,
    fixed: 'left',
  },
  {
    title: t('dataset.fieldKey'),
    dataIndex: 'key',
    width: 80,
  },
  {
    title: t('dataset.fieldType'),
    dataIndex: 'type',
    width: 120,
  },
  {
    title: t('dataset.defaultValue'),
    dataIndex: 'default',
    width: 120,
  },
  {
    title: t('dataset.nullable'),
    dataIndex: 'nullable',
    width: 100,
  },
  {
    title: t('dataset.fieldComment'),
    dataIndex: 'comment',
    width: 200,
  },
  {
    title: t('dataset.aiFieldComment'),
    dataIndex: 'originalAiComment',
    width: 300,
  },
  {
    title: t('dataset.adjustedAiComment'),
    dataIndex: 'aiComment',
    width: 300,
  },
  {
    title: t('dataset.enableField'),
    align: 'center',
    dataIndex: 'action',
    width: 80,
    fixed: 'right',
  },
])

const enabledProportion = computed(() => {
  return `${dataStructureTree.value.filter(item => item.isEnabled).length}/${dataStructureTree.value.length}`
})

const handleDataStructureTreeSelect = (selectedKeys: string[]) => {
  if (selectedKeys.length) {
    currentTable.value = dataStructureTree.value.find(item => item.id === selectedKeys[0])
    getAppTableColumns(selectedKeys[0])
  }
}

const handleUpdateAppTable = (tableId: string, isEnabled: boolean) => {
  dataStructureTree.value.forEach((item) => {
    if (item.id === tableId) {
      item.isEnabled = isEnabled
    }
  })
  updateAppTable(tableId, { isEnabled })
}

const handleGetAppTableAIComment = async (tableId: string) => {
  const data = await getAppTableAIComment(tableId)
  const { table, comment, columns } = data
  if (currentTable.value?.name === table) {
    currentTable.value!.aiComment = comment
  }
  columns?.forEach((item: ITableColumn) => {
    tableColumns.value.forEach((column) => {
      if (column.name === item.name) {
        column.originalAiComment = item.comment
        if (autoReplace.value) {
          column.aiComment = item.comment
        }
      }
    })
  })
  message.success('AI字段注释生成成功')
}

const editPrompt = () => {
  showPromptModal.value = true
}

const _batchUpdateAppTableColumn = () => {
  const columns = tableColumns.value.map((item) => {
    return {
      id: item.id,
      aiComment: item.aiComment,
      originalAiComment: item.originalAiComment,
    }
  })
  updateAppTable(currentTable.value!.id, { aiComment: currentTable.value?.aiComment })
  batchUpdateAppTableColumn(columns as ITableColumn[])
}

const handleUpdateAll = () => {
  Modal.confirm({
    title: t('dataset.updateConfirmTitle'),
    content: t('dataset.updateConfirmContent'),
    okText: t('common.update'),
    cancelText: t('common.cancel'),
    centered: true,
    closable: false,
    onOk: async (close) => {
      await createDataStructure(applicationId as number)
      close()
      handleGetDataStructure()
      message.success(t('dataset.updateStructureSuccess'))
    },
  })
}
</script>

<template>
  <div class="flex h-full">
    <template v-if="dataStructureTree.length">
      <div class="flex flex-col flex-shrink-0 h-full mr-5 overflow-hidden">
        <div class="flex justify-between items-center mb-5 font-medium">
          <div>
            <span class="text-sm">{{ t('dataset.databaseTable') }}</span>
            <span class="ml-2 text-sm text-text-3">{{ enabledProportion }}</span>
          </div>
          <div class="flex">
            <a-button
              class="flex-center mr-2"
              size="small"
              @click="showEditAppTables = !showEditAppTables"
            >
              <span class="text-xs">
                <CheckOutlined v-if="showEditAppTables" />
                <EditOutlined v-else />
                {{ showEditAppTables ? t('dataset.editComplete') : t('common.edit') }}
              </span>
            </a-button>
            <a-button
              class="mr-2"
              size="small"
              @click="editPrompt"
            >
              <span class="text-xs">{{ t('common.promptWord') }}</span>
            </a-button>
            <a-dropdown>
              <a class="ant-dropdown-link" @click.prevent>
                <a-button
                  class="flex-center mr-2"
                  size="small"
                >
                  {{ t('dataset.more') }}
                </a-button>
              </a>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="handleUpdateAll">
                    <CloudSyncOutlined class="mr-1" />
                    <span class="text-xs">{{ t('dataset.updateDatabaseSchema') }}</span>
                  </a-menu-item>
                  <a-menu-item @click="exportAppDatabaseSchema(applicationId, 'json')">
                    <CloudDownloadOutlined class="mr-1" />
                    <span class="text-xs">{{ t('dataset.exportSchemaJson') }}</span>
                  </a-menu-item>
                  <a-menu-item @click="exportAppDatabaseSchema(applicationId, 'ddl')">
                    <CloudDownloadOutlined class="mr-1" />
                    <span class="text-xs">{{ t('dataset.exportSchemaDDL') }}</span>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </div>
        <div class="flex-1 p-5 border rounded-[10px] overflow-y-auto">
          <a-tree
            class="relative ml-[-24px]"
            :tree-data="dataStructureTree"
            :show-icon="false"
            :selected-keys="[currentTable?.id ?? '']"
            @select="handleDataStructureTreeSelect"
          >
            <template #title="node">
              <div class="flex justify-between items-center w-[320px]">
                <span :class="!node.isEnabled && 'text-text-3'">
                  <TableOutlined
                    class="mr-2"
                    :class="node.isEnabled ? 'text-[#009688]' : 'text-text-3'"
                  />
                  {{ node.title }}
                </span>
                <div
                  v-if="showEditAppTables"
                  @click.stop
                >
                  <a-switch
                    v-model:checked="node.isEnabled"
                    size="small"
                    @change="handleUpdateAppTable(node.id, $event)"
                  />
                </div>
              </div>
            </template>
          </a-tree>
        </div>
      </div>
      <div
        v-if="currentTable"
        class="flex-1h-full overflow-hidden"
      >
        <div class="flex justify-between items-center mb-2 text-sm font-medium">
          <div class="flex items-center">
            <TableOutlined class="mr-2 text-[18px]  text-[#009688]" />
            <span class="mr-1">{{ currentTable.name }}</span>
            <span class="flex-shrink-0 font-normal text-xs text-text-3">({{ currentTable.comment }})</span>
          </div>
          <div class="flex-center">
            <div class="flex flex-shrink-0 text-xs">
              <span class="mr-2">{{ t('dataset.autoReplaceAIComment') }}</span>
              <a-switch
                v-model:checked="autoReplace"
                size="small"
              />
            </div>
            <a-button
              class="flex-shrink-0 flex-center min-w-[120px] ml-2"
              size="small"
              :loading="loadingGetAppTableAIComment"
              @click="handleGetAppTableAIComment(currentTable.id)"
            >
              <div class="flex-center text-xs">
                <img
                  class="h-[16px]"
                  src="@/assets/images/ai.png" alt=""
                >
                <span class="ml-1">{{ t('dataset.generateAIComment') }}</span>
              </div>
            </a-button>
            <a-button
              type="primary"
              size="small"
              class="flex-center flex-shrink-0 w-[80px] ml-2"
              @click="_batchUpdateAppTableColumn"
            >
              <div class="text-xs">
                <SaveOutlined />
                <span class="ml-2">{{ t('common.save') }}</span>
              </div>
            </a-button>
          </div>
        </div>
        <a-input
          v-model:value="currentTable.aiComment"
          class="mr-5 mb-3 text-xs text-text-2 font-normal border-0 outline-0 bg-bg-2"
        />
        <a-table
          rowKey="name"
          bordered
          :dataSource="tableColumns"
          :columns="columns"
          :pagination="false"
          size="small"
          :loading="loadingGetTableColumns"
          :scroll="{ y: 'calc(100vh - 223px)', x: 100 }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'originalAiComment'">
              <div class="flex justify-between f-full">
                <span class="text-xs">{{ record.originalAiComment }}</span>
                <RightCircleOutlined
                  v-if="record.originalAiComment"
                  class="cursor-pointer"
                  @click="record.aiComment = record.originalAiComment"
                />
              </div>
            </template>
            <template v-if="column.dataIndex === 'aiComment'">
              <a-textarea
                v-model:value="record.aiComment"
                size="small"
                class="text-xs"
                @press-enter="updateAppTableColumn(record.id, { aiComment: record.aiComment })"
                @blur="updateAppTableColumn(record.id, { aiComment: record.aiComment })"
              />
            </template>
            <template v-if="column.dataIndex === 'action'">
              <a-switch
                v-model:checked="record.isEnabled"
                size="small"
                @change="updateAppTableColumn(record.id, { isEnabled: $event })"
              />
            </template>
          </template>
        </a-table>
      </div>
    </template>
    <div
      v-else-if="!loadingGetDataStructure"
      class="flex-center w-full"
    >
      <div class="flex flex-col">
        <NoData :text="t('dataset.noDataStructure')" />
        <a-button
          type="primary"
          :loading="loadingCreateDataStructure"
          @click="createDataStructure(applicationId)"
        >
          {{ t('dataset.createNow') }}
        </a-button>
      </div>
    </div>
  </div>
  <PromptModal
    v-if="showPromptModal"
    :application-id="applicationId"
    prompt-field-name="columnCommentPrompt"
    :afterClose="() => showPromptModal = false"
  />
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
