<script setup lang="ts">
import {
  DeleteOutlined,
  EditOutlined,
  EllipsisOutlined,
} from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import type { IModel } from '@/types/app'

interface IProps {
  model: IModel
}

const { model } = defineProps<IProps>()
const emit = defineEmits(['edit', 'delete', 'refresh-model-list'])
const { t } = useI18n()
const isEnabled = ref(model.isEnabled)
const { enableDisableModel } = useDeploymentModel()

const handleEnableDisable = async (isEnabled: boolean) => {
  await enableDisableModel(model.id!, isEnabled)
  emit('refresh-model-list')
}
</script>

<template>
  <div class="relative flex items-center w-[360px] h-[160px] p-5 pb-[40px] rounded-[10px] border hover:bg-bg-2/40">
    <img
      class="relative left-[-5px] flex-shrink-0 w-[56px] mr-2"
      src="@/assets/images/model.png"
      alt=""
    >
    <div class="flex flex-col flex-1">
      <span class="mb-1 line-clamp-1 text-text-1 font-medium">{{ model.modelName }}</span>
      <div class="h-[40px] text-xs leading-5 text-text-3 line-clamp-2">
        {{ model.description }}
      </div>
    </div>
    <div class="absolute flex bottom-3 right-5">
      <a-switch
        v-model:checked="isEnabled"
        size="small"
        @change="handleEnableDisable"
      />
    </div>
    <a-dropdown>
      <EllipsisOutlined
        class="absolute top-3 right-5 text-[20px] text-text-2 cursor-pointer"
      />
      <template #overlay>
        <a-menu>
          <a-menu-item @click="emit('edit')">
            <div class="text-sm text-text-2">
              <EditOutlined class="mr-2" />
              <span>{{ t('common.edit') }}</span>
            </div>
          </a-menu-item>
          <a-menu-item @click="emit('delete')">
            <div class="text-sm text-text-2">
              <DeleteOutlined class="mr-2" />
              <span>{{ t('common.delete') }}</span>
            </div>
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </div>
</template>

<style scoped lang="scss">

</style>
