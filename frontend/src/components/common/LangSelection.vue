<script setup lang="ts">
const { locale } = useI18n()
const langOptions = [
  {
    label: 'English',
    value: 'en',
  },
  {
    label: '中文',
    value: 'zh',
  },
]
const langHandle = ({ key }: any) => {
  key && (locale.value = key)
  localStorage.setItem('lang', key)
}
</script>

<template>
  <div
    class="w-[135px] h-[40px] rounded-[8px] border-[1px] border-border-color-1 border-solid flex justify-center items-center"
  >
    <img class="w-[24px]" src="@/assets/images/icon-language.png" alt="">
    <a-dropdown
      :trigger="['click']"
      :arrow="false"
      placement="bottom"
      @open-change="langHandle"
    >
      <a
        class="text-[14px] ml-[10px] mr-[10px] font-[500] text-text-color-1 cursor-pointer"
        @click.prevent
      >
        {{ locale === 'zh' ? '中文' : 'English' }}
        <img class="w-[12px] inline-block" src="@/assets/images/icon-downArrow.png" alt="">
      </a>
      <template #overlay>
        <a-menu @click="langHandle">
          <a-menu-item
            v-for="item in langOptions"
            :key="item.value"
            class="w-[130px]"
          >
            {{ item.label }}
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </div>
</template>

<style lang="scss" scoped></style>
