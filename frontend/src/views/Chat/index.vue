<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import ChatMain from './components/ChatMain/index.vue'
import icon from '@/assets/images/chat.png'
import PageTitle from '@/components/specific/PageTitle.vue'
import PageHeader from '@/components/specific/PageHeader.vue'
import { useAppDatabase } from '@/composables/specific/app'
import NoData from '@/components/common/NoData.vue'

const route = useRoute()
const { t } = useI18n()
const { application, getApplication } = useAppDatabase()
const applicationId = route.params?.applicationId ?? localStorage.getItem('chatApplicationId')
provide('applicationId', applicationId)
applicationId && route.meta.showHeader && getApplication(applicationId as string)
</script>

<template>
  <div class="flex flex-col h-full">
    <template v-if="applicationId">
      <PageHeader
        v-if="route.meta.showHeader"
        class="flex-shrink-0"
      >
        <template #left>
          <div class="flex">
            <PageTitle
              class="mr-5"
              :icon="icon"
            >
              <span>{{ t('chat.title') }}</span>
              <span class="ml-3 pl-3 text-sm border-l">{{ application?.name }}</span>
            </PageTitle>
          </div>
        </template>
      </PageHeader>
      <div class="flex-1 w-full h-full sm:w-full md:w-[80vw] lg:w-[900px] mx-auto overflow-auto">
        <ChatMain />
      </div>
    </template>
    <div
      v-else
      class="flex-center flex-1"
    >
      <NoData :text="t('chat.noApplicationData')" />
    </div>
  </div>
</template>

<style scoped></style>
