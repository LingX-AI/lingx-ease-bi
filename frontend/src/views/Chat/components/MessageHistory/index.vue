<script setup lang="ts">
import { DeleteOutlined } from '@ant-design/icons-vue'
import { useDebounceFn } from '@vueuse/core'
import { useModal, useScrollToBottom } from '@/composables/common'
import ChatMessageList from '@/views/Chat/components/ChatMessageList/index.vue'
import { useMessage } from '@/composables/specific'
import { useUserStore } from '@/store'
import NoData from '@/components/common/NoData.vue'
import DataLoading from '@/components/common/DataLoading.vue'
import { EEventNames, emitter } from '@/mitt'
import type { IMessage } from '@/types/chat'

const emit = defineEmits(['closed'])
const applicationId = inject('applicationId')
const { t } = useI18n()
const { visible, handleCancel } = useModal()
const searchContent = ref('')
const userStore = useUserStore()
const {
  warpRef,
  arrivedState,
} = useScrollToBottom()
const { userInfo } = storeToRefs(userStore)
const {
  loading,
  hasMore,
  total,
  batchDeleteMessage,
  getMessages,
  myMessages,
} = useMessage()

const currentPage = ref(1)
const pageSize = ref(10)
const checkedMessageIds = ref([])
provide('checkedMessageIds', checkedMessageIds)

const getMyMessages = async (isIncremental = false) => {
  const params = {
    application: applicationId,
    user: userInfo.value.id,
    search: searchContent.value,
    page: currentPage.value,
    pageSize: pageSize.value,
    ordering: '-created_at',
  }
  await getMessages(params, isIncremental)
}

getMyMessages()

const debouncedFn = useDebounceFn(() => {
  getMyMessages()
}, 500, {})

const handleChange = () => {
  currentPage.value = 1
  debouncedFn()
}

const deleteMessage = (messageIds: string[]) => {
  myMessages.value = myMessages.value.filter((message: IMessage) => !messageIds.includes(message.id!))
  total.value -= (messageIds.length)
  hasMore.value = myMessages.value.length < total.value
}

watch(() => arrivedState.bottom, (value) => {
  if (value && hasMore.value) {
    currentPage.value += 1
    getMyMessages(true)
  }
})

onMounted(() => {
  emitter.on(EEventNames.MESSAGE_DELETED, deleteMessage)
})

onUnmounted(() => {
  emitter.off(EEventNames.MESSAGE_DELETED, deleteMessage)
})
</script>

<template>
  <a-modal
    :width="916"
    :title="t('chat.chartHistory')"
    :open="visible"
    v-bind="$attrs"
    :footer="false"
    centered
    :afterClose="() => emit('closed')"
    @cancel="handleCancel"
  >
    <div class="flex flex-col pb-5 h-[calc(100vh-140px)] overflow-y-hidden">
      <div class="flex-center flex-shrink-0 p-5">
        <a-input
          v-model:value="searchContent"
          :placeholder="t('chat.searchConversation')"
          size="large"
          allow-clear
          @change="handleChange"
        >
          <template #prefix>
            <span class="iconfont icon-sousuo text-[16px] mx-2 text-text-1" />
          </template>
        </a-input>
        <a-button
          v-if="checkedMessageIds.length"
          size="large"
          type="text"
          class="flex-center ml-3"
          @click="batchDeleteMessage(checkedMessageIds)"
        >
          <template #icon>
            <DeleteOutlined />
          </template>
        </a-button>
      </div>
      <div
        ref="warpRef"
        class="flex-1 px-5 overflow-y-auto"
      >
        <ChatMessageList
          v-if="myMessages.length"
          :messages="myMessages"
          mode="history"
        />
        <NoData
          v-else-if="!loading"
          class="relative top-[calc(50vh-200px)]"
        />
        <DataLoading v-if="loading" />
      </div>
    </div>
  </a-modal>
</template>

<style scoped lang="scss">
</style>
