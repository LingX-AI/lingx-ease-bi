<script setup lang="tsx">
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import DataStructure from './components/DataStructure.vue'
import DeploymentModel from './components/DeploymentModel.vue'
import FineTuningExample from './components/FineTuningExample.vue'
import FineTuningModel from './components/FineTuningModel.vue'
import KnowledgeBase from './components/KnowledgeBase.vue'
import PageHeader from '@/components/specific/PageHeader.vue'
import PageTitle from '@/components/specific/PageTitle.vue'
import icon from '@/assets/images/ai-dataset.png'
import nl2sql from '@/assets/images/nl2sql.png'

const { t } = useI18n()
const route = useRoute()
const applicationId = route.query.id as string
const curDatasetClassification = ref('data_structure')
const { application, getApplication } = useAppDatabase()
getApplication(applicationId)

const datasetClassifications = computed(() => {
  return [
    {
      value: 'data_structure',
      label: t('dataset.dataStructure'),
    },
    {
      value: 'knowledge_base',
      label: t('dataset.knowledgeBase'),
    },
    {
      value: 'fine-tuning_example',
      label: t('dataset.fineTuningExample.fineTuningExamples'),
    },
    {
      value: 'fine-tuning_model',
      label: t('dataset.modelTraining'),
    },
    {
      value: 'deployment_model',
      label: t('dataset.modelDeployment'),
    },
  ]
})

const showFlowChat = () => {
  Modal.info({
    title: t('dataset.flowDescription'),
    width: '70vw',
    content: (<div className="relative left-[-20px] w-full"><img src={nl2sql} alt="" /></div>),
  })
}
</script>

<template>
  <div class="flex flex-col h-full">
    <PageHeader class="flex-shrink-0">
      <template #left>
        <div class="flex">
          <PageTitle
            class="mr-5"
            :icon="icon"
          >
            <span>{{ t('dataset.aiConfig') }}</span>
            <span class="ml-3 pl-3 text-sm border-l">{{ application?.name }}</span>
          </PageTitle>
          <a-segmented
            v-model:value="curDatasetClassification"
            class="w-fit"
            :options="datasetClassifications"
          />
        </div>
      </template>
      <template #right>
        <a-button
          class="flex-center"
          type="text"
          @click="showFlowChat"
        >
          <QuestionCircleOutlined />
          <span>{{ t('dataset.flowDescription') }}</span>
        </a-button>
      </template>
    </PageHeader>
    <div class="flex flex-col flex-1 gap-[16px] p-5 overflow-hidden">
      <div class="flex-1 overflow-hidden">
        <DataStructure
          v-if="curDatasetClassification === 'data_structure'"
          class="h-full overflow-y-auto"
          :application-id="applicationId"
        />
        <KnowledgeBase
          v-else-if="curDatasetClassification === 'knowledge_base'"
          :application-id="applicationId"
        />
        <FineTuningExample
          v-else-if="curDatasetClassification === 'fine-tuning_example'"
          :application-id="applicationId"
        />
        <FineTuningModel
          v-else-if="curDatasetClassification === 'fine-tuning_model'"
          :application-id="applicationId"
        />
        <DeploymentModel
          v-else-if="curDatasetClassification === 'deployment_model'"
          :application-id="applicationId"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
</style>
