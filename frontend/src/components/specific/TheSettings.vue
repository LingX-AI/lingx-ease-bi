<script setup lang="ts">
import { SettingOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import LangSelection from '@/components/common/LangSelection.vue'
import { useUserStore } from '@/store'

const { t } = useI18n()
const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)
const showSettingsModal = ref(false)

const handleClick = () => {
  showSettingsModal.value = true
}
</script>

<template>
  <a-button
    class="flex-center"
    type="text"
    @click="handleClick"
  >
    <SettingOutlined
      class="cursor-pointer"
      style="font-size:20px;color: #5A607F"
    />
  </a-button>
  <a-modal
    v-model:open="showSettingsModal"
    :title="t('settings.title')"
    :mask-closable="false"
    :footer="false"
  >
    <div class="p-5">
      <div class="flex justify-between my-5">
        <span class="text-text-2">{{ t('settings.currentUser') }}</span>
        <span>{{ userInfo.username || userInfo.email }}</span>
      </div>
      <div class="flex justify-between">
        <span class="text-text-2">{{ t('settings.systemLanguage') }}</span>
        <LangSelection class="relative left-[40px] border-none" />
      </div>
      <a-button
        class="mt-10"
        type="primary"
        block
        @click="userStore.logout"
      >
        {{ t('common.logout') }}
      </a-button>
    </div>
  </a-modal>
</template>

<style scoped lang="scss">
</style>
