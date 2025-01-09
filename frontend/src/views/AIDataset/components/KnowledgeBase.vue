<script setup lang="ts">
import DatabaseTableDocument from './DatabaseTableDocument.vue'
import DocumentEmbedding from './DocumentEmbedding.vue'
import RetrievalDocument from './RetrievalDocument.vue'

interface IProps {
  applicationId: string | number
}

const { applicationId } = defineProps<IProps>()

const showRetrievalDocument = ref(false)

provide('showRetrievalDocument', showRetrievalDocument)
</script>

<template>
  <div class="flex h-full">
    <DatabaseTableDocument
      class="flex-shrink-0 mr-3"
      :application-id="applicationId"
    />
    <RetrievalDocument
      v-if="showRetrievalDocument"
      class="flex-1"
      :application-id="applicationId"
    />
    <DocumentEmbedding
      v-else
      class="flex-1"
      :application-id="applicationId"
    />
  </div>
</template>

<style scoped lang="scss">

</style>
