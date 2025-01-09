<script setup lang="ts">
import {
  CopyOutlined,
  DeleteOutlined,
  DownloadOutlined,
  SyncOutlined,
} from '@ant-design/icons-vue'
import type { Ref } from 'vue'
import { useMessage, useMessageAction } from '@/composables/specific'
import { useExportChartData } from '@/composables/common'
import type { IMessage } from '@/types/chat'
import { EDisplayMode } from '@/constants'

const props = withDefaults(defineProps<IProps>(), {
  mode: 'chat',
})

interface IProps {
  message: IMessage
  chartRef: Ref<any>
  mode?: 'chat' | 'history'
}

const { t } = useI18n()
const isPendingResponse = inject('isPendingResponse') as Ref<boolean>
const applicationId = inject('applicationId') as string
const { chat, getMessage } = useMessage({ isPendingResponse })
const { exportExcel, exportCsv } = useExportChartData()
const handleSend = async () => {
  await chat(applicationId, props.message.question, true)
}

const showDownload = computed(() => {
  const { answer } = props.message
  if (!answer) {
    return false
  }
  const displayMode = answer.displayMode || EDisplayMode.TEXT
  return displayMode === 'table' ? true : props.message.answer?.chartOption
})

const isCopied = ref(false)
const { handleCopy, handleDownload } = useMessageAction(props.message)
const { deleteMessage } = useMessage()

const _handleCopy = async () => {
  await handleCopy()
  isCopied.value = true
}

const _handleDownload = (imageType: 'png' | 'jpg') => {
  handleDownload({
    imageType,
    chartRef: props.chartRef,
  })
}

const exportFile = async (fileType: 'excel' | 'csv') => {
  const message: IMessage | undefined = await getMessage(props.message.id!)
  if (!message)
    return
  const queryResult = message.queryResult ?? []
  if (fileType === 'excel')
    exportExcel(queryResult)
  else if (fileType === 'csv')
    exportCsv(queryResult)
}
</script>

<template>
  <div
    class="flex-center"
  >
    <a-tooltip
      v-if="!message.isCancelled"
      placement="top"
      @open-change="(visible:boolean) => !visible && (isCopied = false)"
    >
      <template #title>
        <span>{{ isCopied ? t('chat.copied') : t('chat.copy') }}</span>
      </template>
      <div
        class="flex-center w-7 h-7 rounded-[4px] hover:bg-[#F0F3F6] cursor-pointer"
        @click="_handleCopy"
      >
        <CopyOutlined />
      </div>
    </a-tooltip>
    <a-tooltip
      v-if="mode === 'chat'"
      placement="top"
    >
      <template #title>
        <span>{{ t('chat.regenerate') }}</span>
      </template>
      <div
        class="flex-center w-7 h-7 rounded-[4px] hover:bg-[#F0F3F6] cursor-pointer"
        @click="handleSend"
      >
        <SyncOutlined />
      </div>
    </a-tooltip>
    <a-dropdown v-if="showDownload">
      <div
        class="flex-center w-7 h-7 rounded-[4px] hover:bg-[#F0F3F6] cursor-pointer"
        @click.prevent
      >
        <DownloadOutlined />
      </div>
      <template #overlay>
        <a-menu>
          <template v-if="message.answer?.chartOption">
            <a-menu-item @click="_handleDownload('png')">
              <span>{{ t('chat.downloadPng') }}</span>
            </a-menu-item>
            <a-menu-item @click="_handleDownload('jpg')">
              <span>{{ t('chat.downloadJpg') }}</span>
            </a-menu-item>
          </template>
          <a-menu-item @click="exportFile('excel')">
            <span>{{ t('chat.exportExcel') }}</span>
          </a-menu-item>
          <a-menu-item @click="exportFile('csv')">
            <span>{{ t('chat.exportCsv') }}</span>
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
    <a-tooltip placement="top">
      <template #title>
        <span>{{ t('chat.delete') }}</span>
      </template>
      <div
        class="flex-center w-7 h-7 rounded-[4px] hover:bg-[#F0F3F6] cursor-pointer"
        @click="deleteMessage(message.id!)"
      >
        <DeleteOutlined />
      </div>
    </a-tooltip>
  </div>
</template>

<style scoped lang="scss">

</style>
