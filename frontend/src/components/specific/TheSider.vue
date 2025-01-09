<script setup lang="ts">
import {
  AppstoreOutlined,
  MessageOutlined,
} from '@ant-design/icons-vue'
import TheSettings from './TheSettings.vue'
import ERouteNames from '@/router/route-names'

enum EMenuKey {
  INNER_CHAT = 'inner_chat',
  APP = 'app',
}

interface IMenu {
  key: EMenuKey
  label: string
  icon: any
  routeName: ERouteNames
}

const router = useRouter()
const currentMenu = ref<EMenuKey>(EMenuKey.INNER_CHAT)

const menus = computed<IMenu[]>(() => {
  return [
    { key: EMenuKey.INNER_CHAT, label: '', icon: MessageOutlined, routeName: ERouteNames.INNER_CHAT },
    { key: EMenuKey.APP, label: '', icon: AppstoreOutlined, routeName: ERouteNames.APP },
  ]
})

const handleMenuClick = (menu: IMenu) => {
  currentMenu.value = menu.key
  router.push({
    name: menu.routeName,
  })
}
</script>

<template>
  <div class="flex flex-col h-full items-center w-[80px] border-r py-5">
    <img
      class="w-[40px] h-[40px] mb-5"
      src="../../assets/images/logo-blue.png"
      alt=""
    >
    <div class="flex-1">
      <div
        v-for="item in menus"
        :key="item.key"
        class="w-[46px] h-[46px] flex-center rounded-[10px] mb-2 cursor-pointer hover:bg-[#ECEFF190]"
        :class="{ 'bg-[#ECEFF190]': currentMenu === item.key }"
        @click="handleMenuClick(item)"
      >
        <component
          :is="item.icon"
          style="font-size: 26px; color: #5A607F"
        />
      </div>
    </div>
    <div>
      <TheSettings />
    </div>
  </div>
</template>

<style scoped lang="scss">
</style>
