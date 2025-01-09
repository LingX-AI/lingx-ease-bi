<script setup lang="ts">
import dayjs from 'dayjs'
import { WarningOutlined } from '@ant-design/icons-vue'
import Chart from '@/views/Chat/components/Chart/index.vue'
import MessageAction from '@/views/Chat/components/MessageAction/index.vue'
import ResponseSteps from '@/views/Chat/components/ResponseSteps/index.vue'
import 'highlight.js/styles/a11y-light.css'
import type { IMessage } from '@/types/chat'
import { markdown } from '@/utils/common'

interface IProps {
  message: IMessage
  mode?: 'chat' | 'history'
  previousMessage?: IMessage | undefined
}

const props = withDefaults(defineProps<IProps>(), {
  mode: 'chat',
  isLatestMessage: false,
})
const { t } = useI18n()
const chartRef = ref()
const checked = ref(false)
const checkedMessageIds = inject('checkedMessageIds') as Ref<string[]>
const chartOption = computed(() => {
  const chartOption = props.message.answer?.chartOption
  if (chartOption) {
    return JSON.parse(chartOption)
  }
  return void 0
})

const showMessageAction = computed(() => {
  return !props.message.isPendingResponse
})

const summary = computed(() => {
  return props.message.answer?.summary ?? ''
})

const messageDate = computed(() => {
  const currentMessageDate = dayjs(props.message.createdAt).format('YYYY-MM-DD')
  if (props.previousMessage) {
    const previousMessageDate = dayjs(props.previousMessage.createdAt).format('YYYY-MM-DD')
    if (previousMessageDate === currentMessageDate) {
      return ''
    }
  }
  const isToday = dayjs().format('YYYY-MM-DD') === currentMessageDate
  return isToday ? t('chat.today') : dayjs(props.message.createdAt).format('YYYY-MM-DD')
})

const handleCheck = () => {
  if (checked.value) {
    checkedMessageIds.value.push(props.message.id!)
  }
  else {
    checkedMessageIds.value = checkedMessageIds.value.filter(id => id !== props.message.id)
  }
}

const handleMessageClick = () => {
  if (props.mode === 'history') {
    checked.value = !checked.value
    handleCheck()
  }
}
</script>

<template>
  <template v-if="mode === 'chat'">
    <div class="mb-8">
      <div class="flex justify-end message">
        <div
          class="w-fit py-[15px] px-[20px] text-[14px] rounded-[16px] rounded-br-none border border-border-1 mb-8 bg-[#04346107]"
        >
          {{ message.question }}
        </div>
      </div>
      <div class="message">
        <div class="flex items-center mb-3">
          <img
            class="w-7 h-7 mr-2"
            src="@/assets/images/logo-blue.png"
            alt=""
          >
          <span class="text-[16px] text-text-1 font-[600]">Ease BI</span>
        </div>
        <ResponseSteps
          v-if="!message.isCancelled"
          :steps="message.steps"
          :is-pending-response="!!message.isPendingResponse"
        />
        <div class="relative group">
          <div
            v-if="message.isCancelled"
            class="flex items-center border w-fit px-3 py-1 rounded-[12px] text-warning"
          >
            <WarningOutlined
              class="mr-2"
              style="font-size: 14px"
            />
            <div
              class="text-[14px]"
              v-html="markdown.render(summary)"
            />
          </div>
          <div
            v-else-if="summary"
            class="text-[14px]"
            v-html="markdown.render(summary)"
          />
          <Chart
            v-if="chartOption"
            ref="chartRef"
            class="mt-5"
            :option="chartOption"
          />
          <ChartsSkeleton v-else-if="message.isChartGenerating" />
          <div
            v-if="showMessageAction"
            class="absolute flex justify-start w-full left-0 opacity-0 pt-2 group-hover:opacity-100"
          >
            <MessageAction
              :message="message"
              :chart-ref="chartRef"
            />
          </div>
        </div>
      </div>
    </div>
  </template>
  <template v-else>
    <div
      v-if="mode === 'history' && messageDate"
      class="flex-center w-full mb-3"
    >
      <div class="flex-1 h-[1px] bg-[#9898A340]" />
      <span class="flex-shrink-0 text-[12px] text-[#9898A3] mx-4">
        {{ messageDate }}
      </span>
      <div class="flex-1 h-[1px] bg-[#9898A340]" />
    </div>
    <a-popover
      placement="bottomRight"
      :arrow="false"
      :destroyTooltipOnHide="true"
      :mouseEnterDelay="0.8"
      :autoAdjustOverflow="false"
    >
      <template #content>
        <div
          v-if="showMessageAction"
          class="flex justify-start w-full"
        >
          <MessageAction
            :message="message"
            :chart-ref="chartRef"
            mode="history"
          />
        </div>
      </template>
      <div
        class="mb-2 rounded-[12px] hover:bg-[#0434610a] group"
        :class="mode === 'history' && 'cursor-pointer'"
        @click="handleMessageClick"
      >
        <div class="flex items-center message p-2 rounded-[12px]">
          <div
            v-if="checkedMessageIds.length"
            class="mr-3"
          >
            <a-checkbox
              v-model:checked="checked"
              @change="handleCheck"
            />
          </div>
          <div
            v-else
            class="mr-3 hidden group-hover:block"
          >
            <a-checkbox
              v-model:checked="checked"
              @change="handleCheck"
            />
          </div>
          <img
            class="w-7 h-7 mr-3"
            src="@/assets/images/user-avatar.png"
            alt=""
          >
          <div class="w-fit text-[14px] rounded-[16px] rounded-br-none">
            {{ message.question }}
          </div>
        </div>
        <div class="message flex p-2 rounded-[12px]">
          <img
            class="w-7 h-7 mr-2"
            src="@/assets/images/logo-blue.png"
            alt=""
          >
          <div class="group flex-1">
            <div
              v-if="summary"
              class="markdown-body inline-block text-[14px]"
              :class="message.isCancelled && 'text-warning'"
              v-html="markdown.render(summary)"
            />
            <Chart
              v-if="chartOption"
              ref="chartRef"
              class="mt-5"
              :option="chartOption"
            />
          </div>
        </div>
      </div>
    </a-popover>
  </template>
</template>

<style lang="scss" scoped>
:deep(div.message) {
  li::marker {
    color: #9898A3;
  }

  table {
    display: block;
    width: fit-content;
    max-width: 900px;
    border-radius: 10px;
    border-collapse: separate;
    border-spacing: 0;
    margin: 10px 0;
    background-color: #FFFFFF;
    overflow: hidden;
    overflow-x: auto;
    border: 1px solid #CFD8DC;
  }

  th,
  td {
    border-top: 1px solid #CFD8DC;
    border-right: 1px solid #CFD8DC;
    padding: 10px 20px;
    font-size: 14px;
  }

  th {
    border-top: none;
    background-color: #CFD8DC50;
  }

  tr {
    td:last-child {
      border-right: none;
    }

    th:last-child {
      border-right: none;
    }
  }

  p,
  li {
    line-height: 2em;
  }

  p:not(:last-child) {
    margin-bottom: 14px;
  }

  ol,
  ul {
    padding: 0 20px;
    list-style: unset;
  }

  a {
    text-decoration: underline;
    color: #1E88E5;
    cursor: pointer;
  }

  .markdown-body {
    overflow-x: auto;
    max-width: 100%;
  }
}

:deep(code.hljs) {
  display: inline-block;
  margin: 0 6px;
  padding: 0 6px;
  border-radius: 6px;
}

:deep(div.message pre) {
  position: relative;
  margin: 16px 0;

  code.hljs {
    display: block;
    margin: 0;
    padding: 50px 20px 24px 20px;
    border-radius: 10px;
  }
}
</style>
