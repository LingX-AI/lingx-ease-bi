<script setup lang="ts">
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import enUS from 'ant-design-vue/es/locale/en_US'
import { useExternalLocale } from '@/composables/specific/locale'
import { useAuth } from '@/composables/specific/auth'
import TheSider from '@/components/specific/TheSider.vue'

dayjs.locale('zh-cn')

const route = useRoute()
const { locale: i18nLocale } = useI18n()
useExternalLocale()
const { listenAppUserIdChange } = useAuth()
const colorPrimary = '#1766E1'
const theme = {
  token: {
    colorPrimary,
    colorLink: colorPrimary,
    colorInfo: colorPrimary,
    colorInfoText: colorPrimary,
  },
}
message.config({
  maxCount: 1,
})

const showSidebar = computed(() => {
  const hideSidebar = route.meta.hideSidebar
  // if (hideSidebar === undefined) {
  //   return false
  // }
  return !hideSidebar
})

const locale = computed(() => {
  return i18nLocale.value === 'zh' ? zhCN : enUS
})

listenAppUserIdChange()
</script>

<template>
  <a-config-provider
    :wave="{ disabled: true }"
    :theme="theme"
    :form="{
      colon: false,
    }"
    :locale="locale"
  >
    <div class="flex w-100% h-[100vh]">
      <TheSider v-if="showSidebar" />
      <div class="flex-1 h-full overflow-hidden">
        <router-view />
      </div>
    </div>
  </a-config-provider>
</template>

<style lang="scss">
#nprogress {
  .bar {
    background: v-bind("colorPrimary") !important;
  }
  .peg {
    box-shadow: 0 0 10px v-bind("colorPrimary"), 0 0 5px v-bind("colorPrimary");
  }
}
</style>
