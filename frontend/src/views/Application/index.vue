<script setup lang="ts">
import { FolderAddOutlined } from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import AppCard from './components/AppCard.vue'
import AppForm from './components/AppForm.vue'
import SuggestedQuestionsModal from './components/SuggestedQuestionsModal.vue'
import PageHeader from '@/components/specific/PageHeader.vue'
import PageTitle from '@/components/specific/PageTitle.vue'
import databaseIcon from '@/assets/images/database.png'
import PromptModal from '@/views/AIDataset/components/PromptModal.vue'

const { t } = useI18n()
const currentAppId = ref<string | number>('')
const showAppForm = ref(false)
const showPromptModal = ref(false)
const showSuggestedQuestionsModal = ref(false)
const { appDatabases, getAppDatabases, deleteApplication } = useAppDatabase()
getAppDatabases()

const handleAdd = () => {
  currentAppId.value = ''
  showAppForm.value = true
}
const handleEdit = (id: string | number) => {
  currentAppId.value = id
  showAppForm.value = true
}

const handleShowPrompt = (id: string | number) => {
  currentAppId.value = id
  showPromptModal.value = true
}

const handleDelete = (id: string | number) => {
  Modal.confirm({
    title: t('common.deleteConfirm'),
    content: t('common.deleteTip'),
    centered: true,
    onOk: async () => {
      const res = await deleteApplication(id)
      if (res) {
        getAppDatabases()
      }
    },
  })
}

const handleShowSuggestedQuestions = (id: string | number) => {
  currentAppId.value = id
  showSuggestedQuestionsModal.value = true
}
</script>

<template>
  <div class="">
    <PageHeader>
      <template #left>
        <PageTitle :icon="databaseIcon">
          {{ t('application.databaseList') }}
        </PageTitle>
      </template>
    </PageHeader>
    <div class="flex gap-[16px] flex-wrap p-5">
      <AppCard
        v-for="appDatabase in appDatabases"
        :key="appDatabase.id"
        :app-database="appDatabase"
        @edit="handleEdit(appDatabase.id)"
        @show-prompt="handleShowPrompt(appDatabase.id)"
        @show-suggested-questions="handleShowSuggestedQuestions(appDatabase.id)"
        @delete="handleDelete(appDatabase.id)"
      />
      <div
        class="flex-center w-[360px] h-[160px] p-5 rounded-[10px] border cursor-pointer hover:bg-bg-2/40"
        @click="handleAdd"
      >
        <FolderAddOutlined class="text-[40px] text-text-2" />
      </div>
    </div>
  </div>
  <AppForm
    v-if="showAppForm"
    :id="currentAppId"
    :afterClose="() => showAppForm = false"
    @saved="getAppDatabases"
  />
  <PromptModal
    v-if="showPromptModal"
    :application-id="currentAppId"
    show-all-prompt
    :afterClose="() => showPromptModal = false"
  />
  <SuggestedQuestionsModal
    v-if="showSuggestedQuestionsModal"
    :application-id="currentAppId"
    :afterClose="() => showSuggestedQuestionsModal = false"
  />
</template>

<style scoped lang="scss"></style>
