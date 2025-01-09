<script setup lang="ts">

</script>

<template>
  <div class="flex justify-between items-center h-[68px] px-5 border-b">
    <div>
      <slot name="left" />
    </div>
    <div>
      <slot name="right" />
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
