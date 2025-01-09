<script setup lang="ts">
const attrs = useAttrs()

console.log(attrs.icon)
</script>

<template>
  <p class="flex items-center text-[#616161] font-medium">
    <img
      class="w-[30px] mr-2"
      :src="attrs.icon as string" alt=""
    >
    <slot />
  </p>
</template>

<style scoped lang="scss">
</style>
