<script setup lang="ts">
import type { Form } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import { useModal } from '@/composables/common'
import { useDeploymentModel } from '@/composables/specific/app'
import type { IModel } from '@/types/app'

interface IProps {
  model: IModel
}

const { model } = defineProps<IProps>()
const emit = defineEmits(['saved'])
const { t } = useI18n()
const { visible, handleCancel } = useModal()
const { updateModel } = useDeploymentModel()
const formRef = ref<InstanceType<typeof Form> | null>(null)
const formData = reactive<IModel>({
  id: model.id,
  modelName: model.modelName,
  description: model.description,
  isEnabled: model.isEnabled,
})

const handleSaveApp = async () => {
  await (formRef.value as any).validate()
  const res = await updateModel(formData.id as string, formData)
  if (res) {
    emit('saved')
    handleCancel()
    message.success(t('dataset.deploymentModel.saveSuccess'))
  }
}
</script>

<template>
  <a-modal
    v-model:open="visible"
    :title="t('dataset.deploymentModel.updateModel')"
    width="600px"
    centered
    v-bind="$attrs"
    :ok-text="t('common.save')"
    @cancel="handleCancel"
    @ok="handleSaveApp"
  >
    <div class="p-10 max-h-[80vh] overflow-y-auto">
      <a-form
        ref="formRef"
        class="w-full"
        :model="formData"
        layout="vertical"
      >
        <a-form-item
          :label="t('dataset.deploymentModel.modelName')"
          name="modelName"
          :rules="[{ required: true, message: t('dataset.deploymentModel.modelNameRequired') }]"
        >
          <a-input
            v-model:value="formData.modelName"
            disabled
          />
        </a-form-item>
        <a-form-item
          :label="t('dataset.deploymentModel.description')"
          name="description"
          :rules="[{ required: true, message: t('dataset.deploymentModel.descriptionRequired') }]"
        >
          <a-textarea
            v-model:value="formData.description"
            :auto-size="{
              minRows: 3,
              maxRows: 8,
            }"
          />
        </a-form-item>
      </a-form>
    </div>
  </a-modal>
</template>

<style scoped lang="scss">
</style>
