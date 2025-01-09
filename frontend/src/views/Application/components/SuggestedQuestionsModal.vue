<script setup lang="ts">
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import type { IAppSuggestedQuestion } from '@/types/app'
import { useAppDatabase } from '@/composables/specific/app'

interface IProps {
  applicationId: string | number
}

const props = defineProps<IProps>()
const { visible, handleCancel } = useModal()
const { t } = useI18n()
const loading = ref(false)

const {
  getSuggestedQuestions,
  updateSuggestedQuestions,
} = useAppDatabase()

const questions = ref<IAppSuggestedQuestion[]>([
  { applicationId: Number(props.applicationId), question: '' },
])

const init = async () => {
  const data = await getSuggestedQuestions(props.applicationId)
  if (data?.length) {
    questions.value = data
  }
}

init()

const handleAdd = () => {
  if (questions.value.length >= 3) {
    return
  }
  questions.value.push({
    applicationId: Number(props.applicationId),
    question: '',
  })
}

const handleRemove = (index: number) => {
  questions.value.splice(index, 1)
}

const handleSave = async () => {
  if (questions.value.some(q => !q.question.trim())) {
    message.warning(t('application.suggestedQuestions.emptyWarning'))
    return
  }

  loading.value = true
  const _questions = questions.value.map(item => item.question)
  const success = await updateSuggestedQuestions(props.applicationId, _questions)
  if (success) {
    message.success(t('application.suggestedQuestions.updateSuccess'))
  }
  loading.value = false

  if (success) {
    handleCancel()
  }
}
</script>

<template>
  <a-modal
    :visible="visible"
    :title="t('application.suggestedQuestions.title')"
    :confirm-loading="loading"
    v-bind="$attrs"
    @ok="handleSave"
    @cancel="handleCancel"
  >
    <div class="space-y-4 p-5">
      <div
        v-for="(question, index) in questions"
        :key="index"
        class="flex items-center gap-2"
      >
        <a-textarea
          v-model:value="question.question"
          :placeholder="t('application.suggestedQuestions.placeholder')"
          :rows="3"
        />
        <MinusCircleOutlined
          class="text-danger cursor-pointer"
          @click="handleRemove(index)"
        />
      </div>

      <a-button
        v-if="questions.length < 3"
        type="dashed"
        block
        @click="handleAdd"
      >
        <PlusOutlined />
        {{ t('application.suggestedQuestions.add') }}
      </a-button>
    </div>
  </a-modal>
</template>

<style lang="scss"></style>
