<script setup lang="ts">
import { FolderAddOutlined } from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import ModelCard from './ModelCard.vue'
import DeploymentModelModal from './DeploymentModelModal.vue'
import ModelForm from './ModelForm.vue'
import { useDeploymentModel } from '@/composables/specific/app'
import type { IModel } from '@/types/app'

interface IProps {
  applicationId: string | number
}

const { applicationId } = defineProps<IProps>()
const { t } = useI18n()
const openDeploymentModelForm = ref(false)
const showModelForm = ref(false)
const currentModel = ref<IModel>()
const {
  models,
  getModels,
  deleteModel,
} = useDeploymentModel()

getModels(applicationId)

const handleEdit = (model: IModel) => {
  currentModel.value = model
  showModelForm.value = true
}

const handleDelete = (id: string) => {
  Modal.confirm({
    title: t('common.deleteConfirm'),
    content: t('common.deleteTip'),
    centered: true,
    onOk: async () => {
      const res = await deleteModel(id)
      if (res) {
        getModels(applicationId)
      }
    },
  })
}
</script>

<template>
  <div class="w-full h-full flex flex-wrap content-start gap-[16px]">
    <ModelCard
      v-for="model in models"
      :key="model.id"
      :model="model"
      @edit="handleEdit(model)"
      @delete="handleDelete(model.id!)"
      @refresh-model-list="getModels(applicationId)"
    />
    <div
      class="flex-center w-[360px] h-[160px] p-5 rounded-[10px] border cursor-pointer hover:bg-bg-2/40"
      @click="openDeploymentModelForm = true"
    >
      <FolderAddOutlined class="text-[40px] text-text-2" />
    </div>
  </div>
  <ModelForm
    v-if="showModelForm"
    :model="currentModel!"
    :afterClose="() => showModelForm = false"
    @saved="getModels(applicationId)"
  />
  <DeploymentModelModal
    v-if="openDeploymentModelForm"
    :applicationId="applicationId"
    :after-close="() => openDeploymentModelForm = false"
    @refresh-model-list="getModels(applicationId)"
  />
</template>

<style scoped lang="scss"></style>
