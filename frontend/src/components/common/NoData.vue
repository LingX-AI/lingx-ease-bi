<script setup lang="ts">
import { Empty } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'

interface IProps {
  imageSrc?: string
  text?: string
}

const { imageSrc = Empty.PRESENTED_IMAGE_SIMPLE, text } = defineProps<IProps>()
const { t } = useI18n()
</script>

<template>
  <div class="flex-center">
    <a-empty
      class="flex flex-col items-center"
      :image="imageSrc"
      :image-style="{
        height: '60px',
      }"
    >
      <template #description>
        <span>{{ text || t('common.noData') }}</span>
      </template>
    </a-empty>
  </div>
</template>

<style scoped lang="scss">

</style>
