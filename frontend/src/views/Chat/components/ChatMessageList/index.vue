<script setup lang="ts">
import ChatMessageItem from '@/views/Chat/components/ChatMessageItem/index.vue'
import type { IMessage } from '@/types/chat'

interface IProps {
  messages: IMessage[]
  mode?: 'chat' | 'history'
}
withDefaults(defineProps<IProps>(), {
  messages: () => [],
  mode: 'chat',
})
</script>

<template>
  <div>
    <ChatMessageItem
      v-for="(message, index) in messages"
      :key="message.id || message.taskId"
      :message="message"
      :mode="mode"
      :previous-message="messages[index - 1]"
    />
    <div class="pb-20" />
  </div>
</template>

<style scoped>
</style>
