<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/specific/auth'
import Chat from '@/views/Chat/index.vue'
import LangSelection from '@/components/common/LangSelection.vue'

const { auth } = useAuth()
const route = useRoute()
const showChat = ref(false)
const applicationId = route.params?.applicationId ?? localStorage.getItem('chatApplicationId')

const handleAuth = async () => {
  await auth(applicationId as string)
  showChat.value = true
}

const showLangSelection = computed(() => route.name === 'chat')

handleAuth()
</script>

<template>
  <div class="relative h-full">
    <div
      v-if="showLangSelection"
      class="absolute top-4 right-4 z-10"
    >
      <LangSelection />
    </div>

    <Chat v-if="showChat" />
    <div
      v-else
      class="flex justify-center items-center w-[100vw] h-[100vh]"
    >
      <div class="flex-center">
        <img
          class="w-7 h-7 mr-2"
          src="@/assets/images/logo-blue.png"
          alt=""
        >
        <span class="text-lg text-text-2 font-medium">LingX AI</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
