<script setup lang="ts">
const { t } = useI18n()
</script>

<template>
  <div class="w-full p-5 border border-border-1 rounded-[16px] mt-5">
    <a-skeleton
      active
      :paragraph="{ rows: 4 }"
    />
    <span class="inline-block mt-5 text-text-3 text-xs">{{ t('chat.generatingChart') }}</span>
  </div>
</template>

<style scoped lang="scss">

</style>
