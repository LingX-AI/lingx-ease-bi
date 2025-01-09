<script setup lang="tsx">
import {
  BuildOutlined,
  CopyOutlined,
  DeleteOutlined,
  EditOutlined,
  EllipsisOutlined,
  InfoCircleOutlined,
  LinkOutlined,
  MessageOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import ERouteNames from '@/router/route-names'
import type { IAppDatabase } from '@/types/app'
import { useCopy } from '@/composables/common'

interface IProps {
  appDatabase: IAppDatabase
}

const { appDatabase } = defineProps<IProps>()
const emit = defineEmits(['edit', 'delete', 'show-prompt', 'show-suggested-questions'])
const { handleCopy } = useCopy()
const { t } = useI18n()
const router = useRouter()
const handleToAIDataset = () => {
  router.push({
    name: ERouteNames.AI_DATASET,
    query: { id: appDatabase.id },
  })
}

const link = `${location.protocol}//${location.host}/chat/${appDatabase.id}`

const handleToChat = () => {
  localStorage.setItem('chatApplicationId', `${appDatabase.id}`)
  router.push({
    name: ERouteNames.INNER_CHAT,
    params: { applicationId: appDatabase.id },
  })
}

const showLink = () => {
  Modal.info({
    title: t('application.externalLink'),
    width: 600,
    content: (
      <div className="relative left-[-20px] py-5">
        <p className="mb-5 p-3 bg-bg-2 rounded text-sm">
          {t('application.externalLinkDesc')}
        </p>
        <p>
          <LinkOutlined class="mr-2" />
          <span>
            {link}
          </span>
          <CopyOutlined
            class="ml-2"
            onClick={() => handleCopy(link)}
          />
        </p>
      </div>
    ),
  })
}
</script>

<template>
  <div class="relative flex items-center w-[360px] h-[160px] p-5 pb-[40px] rounded-[10px] border hover:bg-bg-2/40">
    <img
      class="relative left-[-5px] flex-shrink-0 w-[56px] mr-2"
      src="@/assets/images/database1.png"
      alt=""
    >
    <div class="flex flex-col flex-1">
      <span class="mb-1 line-clamp-1 text-text-1 font-medium">{{ appDatabase.name }}</span>
      <div class="h-[40px] text-xs leading-5 text-text-3 line-clamp-2">
        {{ appDatabase.description }}
      </div>
    </div>
    <div class="absolute flex bottom-3 right-5">
      <a-button
        class="flex-center mr-2"
        size="small"
        @click="handleToAIDataset"
      >
        <BuildOutlined />
        {{ t('application.aiConfig') }}
      </a-button>
      <a-button
        class="flex-center"
        size="small"
        type="primary"
        @click="handleToChat"
      >
        <MessageOutlined />
        {{ t('application.startChat') }}
      </a-button>
    </div>
    <a-dropdown>
      <EllipsisOutlined class="absolute top-3 right-5 text-[20px] text-text-2 cursor-pointer" />
      <template #overlay>
        <a-menu>
          <a-menu-item @click="emit('edit')">
            <div class="text-sm text-text-2">
              <EditOutlined class="mr-2" />
              <span>{{ t('common.edit') }}</span>
            </div>
          </a-menu-item>
          <a-menu-item @click="emit('show-prompt')">
            <div class="text-sm text-text-2">
              <InfoCircleOutlined class="mr-2" />
              <span>{{ t('common.promptWord') }}</span>
            </div>
          </a-menu-item>
          <a-menu-item @click="showLink">
            <div class="text-sm text-text-2">
              <LinkOutlined class="mr-2" />
              <span>{{ t('application.externalLink') }}</span>
            </div>
          </a-menu-item>
          <a-menu-item @click="emit('delete')">
            <div class="text-sm text-text-2">
              <DeleteOutlined class="mr-2" />
              <span>{{ t('common.delete') }}</span>
            </div>
          </a-menu-item>
          <a-menu-item @click="emit('show-suggested-questions')">
            <div class="text-sm text-text-2">
              <QuestionCircleOutlined class="mr-2" />
              <span>{{ t('application.suggestedQuestions.menuTitle') }}</span>
            </div>
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </div>
</template>

<style scoped lang="scss"></style>
