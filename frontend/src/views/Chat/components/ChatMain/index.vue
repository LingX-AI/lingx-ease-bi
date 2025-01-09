<script setup lang="ts">
import dayjs from 'dayjs'
import ChatInput from '@/views/Chat/components/ChatInput/index.vue'
import BuiltInQuestion from '@/views/Chat/components/BuiltInQuestion/index.vue'
import ChatMessageList from '@/views/Chat/components/ChatMessageList/index.vue'
import { EEventNames, emitter } from '@/mitt'
import { useMessage } from '@/composables/specific'
import { useUserStore } from '@/store'
import { useScrollToBottom } from '@/composables/common'
import type { IMessage } from '@/types/chat'

const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)
const isPendingResponse = ref(false)
const applicationId = inject('applicationId') as string
provide('isPendingResponse', isPendingResponse)

const { getMessages, myMessages } = useMessage()
const {
  warpRef,
  scrollToBottom,
  scrollY,
} = useScrollToBottom()

const getMyMessages = async ({
  needToScrollToBottom = false,
  params = {
    application: applicationId || undefined,
    user: userInfo.value.id,
    pageSize: 10000,
    createdDateAfter: dayjs().format('YYYY-MM-DD'),
    createdDateBefore: dayjs().format('YYYY-MM-DD'),
  },
} = {}) => {
  await getMessages(params)
  if (needToScrollToBottom && myMessages.value.length)
    scrollToBottom()
}

getMyMessages({ needToScrollToBottom: true })

const handleAddNewMessage = (message: IMessage) => {
  const index = myMessages.value.findIndex(item => item.taskId && item.taskId === message.taskId)
  if (index !== -1) {
    myMessages.value[index] = { ...myMessages.value[index], ...message }
    scrollToBottom()
    return
  }
  myMessages.value.push(message)
  scrollToBottom()
}

let warpHeight = 0
const showToBottomButton = ref(false)
watch(scrollY, (value) => {
  if (value > warpHeight) {
    warpHeight = value as number
  }
  showToBottomButton.value = warpHeight - value > 400
})

onMounted(() => {
  emitter.on(EEventNames.NEW_MESSAGE, handleAddNewMessage)
  emitter.on(EEventNames.MESSAGE_CANCELLED, getMyMessages)
  emitter.on(EEventNames.MESSAGE_DELETED, getMyMessages)
})

onUnmounted(() => {
  emitter.off(EEventNames.NEW_MESSAGE, handleAddNewMessage)
  emitter.off(EEventNames.MESSAGE_CANCELLED, getMyMessages)
  emitter.off(EEventNames.MESSAGE_DELETED, getMyMessages)
})
</script>

<template>
  <div class="relative flex flex-col w-full h-full pb-6 overflow-hidden">
    <div
      ref="warpRef"
      class="flex-1 message-list overflow-y-auto"
    >
      <BuiltInQuestion
        :applicationId="applicationId"
        class="flex-shrink-0 pt-12"
      />
      <ChatMessageList
        :messages="myMessages"
        class="flex-1"
      />
      <!--      <div class="w-fit pb-20"> -->
      <!--        <DataLoading -->
      <!--          v-if="isPendingResponse" -->
      <!--          size="default" -->
      <!--          color="#043461" -->
      <!--        /> -->
      <!--      </div> -->
      <div
        v-if="showToBottomButton"
        class="absolute to-bottom right-0 bottom-[110px] flex-center w-10 h-10 rounded-[100px] bg-white cursor-pointer"
        @click="scrollToBottom(true)"
      >
        <span class="iconfont icon-xiajiantou-" />
      </div>
    </div>
    <ChatInput class="flex-shrink-0" />
  </div>
</template>

<style lang="scss" scoped>
div.to-bottom {
  box-shadow: 0 2px 8px 0 rgba(178, 183, 197, 0.25);
}

div.message-list {
  &::-webkit-scrollbar {
    display: none;
  }
}
</style>
