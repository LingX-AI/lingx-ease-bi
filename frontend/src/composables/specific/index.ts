import type { Ref } from 'vue'
import { v4 as uuid4 } from 'uuid'
import { useClipboard } from '@vueuse/core'
import { Modal, message as showMessage } from 'ant-design-vue'
import { SSE } from 'sse.js'
import { EEventNames, emitter } from '@/mitt'
import {
  batchDeleteMessageApi,
  cancelChatApi,
  chatApi,
  deleteMessageApi,
  generateChartOptionApi,
  getMessageApi,
  getMyMessagesApi,
} from '@/services/apis/chat'
import type { IMessage, IStep } from '@/types/chat'
import { EStepNames } from '@/types/chat'
import { EDisplayMode } from '@/constants'
import { useUserStore } from '@/store'

let lastMessageTaskId = ''
let source: typeof SSE
export const useMessage = ({ isPendingResponse = ref<boolean>(false) } = {}) => {
  const { t } = useI18n()
  const store = useUserStore()
  const loading = ref(false)
  const hasMore = ref(false)
  const total = ref(0)
  const myMessages = ref<IMessage[]>([])
  const getMessages = async (
    params: Record<string, any> = {},
    isIncremental = false,
  ) => {
    loading.value = true
    const resData = await getMyMessagesApi(params).finally(() => {
      loading.value = false
    })
    if (resData?.code === 0) {
      const data = resData?.data
      const newMessages = resData?.data?.results ?? []
      myMessages.value = isIncremental ? [...myMessages.value, ...newMessages] : newMessages
      hasMore.value = !!data?.next
      total.value = data.count ?? 0
    }
  }

  const getMessage = async (messageId: string) => {
    const res = await getMessageApi(messageId)
    if (res?.code === 0) {
      return res.data
    }
  }

  const deleteMessage = async (messageId: string) => {
    const res = await deleteMessageApi(messageId)
    if (res?.code === 0) {
      emitter.emit(EEventNames.MESSAGE_DELETED, messageId)
      showMessage.success('Delete success')
    }
  }

  const batchDeleteMessage = async (messageIds: string[]) => {
    Modal.confirm({
      title: t('common.deleteConfirm'),
      content: t('common.deleteTip'),
      okText: t('chat.delete'),
      cancelText: t('common.cancel'),
      centered: true,
      onOk: async () => {
        const res = await batchDeleteMessageApi(messageIds)
        if (res?.code === 0) {
          emitter.emit(EEventNames.MESSAGE_DELETED, messageIds)
          showMessage.success('Delete success')
        }
      },
    })
  }

  const chatNoStream = async (newMessage: IMessage) => {
    const payload = { question: newMessage.question, taskId: newMessage.taskId }
    const resData = await chatApi(payload)
      .finally(() => {
        isPendingResponse.value = false
        newMessage.isPendingResponse = false
      })
    if (resData?.code !== 0)
      return
    const _newMessage = resData.data
    if (!_newMessage)
      return
    if (_newMessage.answer.displayMode === EDisplayMode.CHART)
      _newMessage.isChartGenerating = true
    const __newMessage = { ...newMessage, ..._newMessage }
    emitter.emit(EEventNames.NEW_MESSAGE, __newMessage)
    if (!_newMessage.isChartGenerating)
      return
    const _resData = await generateChartOptionApi({ messageId: _newMessage.id }).finally(() => {
      __newMessage.isChartGenerating = false
    })
    const chartOptionMessage = _resData?.data ?? {}
    const _chartOptionMessage = { ...__newMessage, ...chartOptionMessage }
    emitter.emit(EEventNames.NEW_MESSAGE, _chartOptionMessage)
  }

  const chatStream = (newMessage: IMessage) => {
    const baseUrl = import.meta.env.VITE_API_ENDPOINT
    const payload = {
      question: newMessage.question,
      taskId: newMessage.taskId,
      applicationId: newMessage.applicationId,
    }
    source = new SSE(`${baseUrl}/chat_stream`, {
      headers: { 'Content-Type': 'application/json', 'Authorization': store.token },
      payload: JSON.stringify(payload),
      method: 'POST',
    })
    const handler = async (e: Record<string, any>) => {
      const stepData = JSON.parse(e?.data ?? '[]')
      newMessage.steps = stepData
      const latestStep = stepData[stepData.length - 1]
      newMessage.id = latestStep.id
      newMessage.taskId = latestStep.taskId
      if (latestStep?.step === EStepNames.ANSWER_GENERATOR_AGENT) {
        newMessage.answer = latestStep.result
      }
      if (latestStep?.isFinalCompleted) {
        newMessage.answer = latestStep.answer
        newMessage.isPendingResponse = false
        isPendingResponse.value = false
        if (newMessage.answer?.displayMode === EDisplayMode.CHART)
          newMessage.isChartGenerating = true
        emitter.emit(EEventNames.NEW_MESSAGE, newMessage)
        if (newMessage.isChartGenerating) {
          console.log('newMessage.steps', newMessage.steps)
          const question_step = newMessage.steps!.find((step: IStep) => step.step === EStepNames.QUESTION_AGENT) as Record<string, any>
          const language = question_step?.result?.language ?? 'English'
          const _resData = await generateChartOptionApi({ messageId: newMessage.id, language }).finally(() => {
            newMessage.isChartGenerating = false
          })
          const chartOptionMessage = _resData?.data ?? {}
          const _newMessage = { ...newMessage, ...chartOptionMessage }
          emitter.emit(EEventNames.NEW_MESSAGE, _newMessage)
          return
        }
      }
      emitter.emit(EEventNames.NEW_MESSAGE, newMessage)
    }
    source.addEventListener('message', handler)
    source.addEventListener('close', () => {
      isPendingResponse.value = false
    })
    source.stream()
  }

  const chat = async (applicationId: string, question: Ref<string> | string, stream = true) => {
    if (isPendingResponse.value) {
      return
    }
    const _question = isRef(question) ? question.value.trim() : question.trim()
    if (!_question)
      return
    if (isRef(question)) {
      question.value = ''
    }
    const newMessage: IMessage = {
      taskId: uuid4(),
      question: _question,
      applicationId,
      isPendingResponse: true,
    }
    emitter.emit(EEventNames.NEW_MESSAGE, newMessage)
    lastMessageTaskId = newMessage.taskId!
    isPendingResponse.value = true
    stream ? chatStream(newMessage) : await chatNoStream(newMessage)
  }

  const cancelChat = async () => {
    source?.close()
    if (!lastMessageTaskId) {
      return
    }
    const resData = await cancelChatApi({ taskId: lastMessageTaskId })
      .finally(() => {
        isPendingResponse.value = false
      })
    if (resData?.code === 0) {
      emitter.emit(EEventNames.MESSAGE_CANCELLED)
    }
  }

  return {
    loading,
    hasMore,
    total,
    myMessages,
    getMessage,
    getMessages,
    deleteMessage,
    batchDeleteMessage,
    isPendingResponse,
    chat,
    cancelChat,
  }
}

export const useMessageAction = (message: IMessage) => {
  const { copy } = useClipboard()
  const handleCopy = async () => {
    const content = message.answer?.summary
    content && await copy(content)
  }
  const handleDownload = (
    {
      imageType = 'png',
      pixelRatio = 2,
      chartRef,
    }: {
      imageType?: 'jpg' | 'png'
      pixelRatio?: number
      chartRef: any
    },
  ) => {
    const dataURL = chartRef?.getDataURL({
      type: imageType,
      pixelRatio,
      backgroundColor: '#FFFFFF',
    })
    let link: any = document.createElement('a')
    link.href = dataURL
    link.download = `Chart image.${imageType}`
    link.click()
    link = null
  }
  return {
    handleCopy,
    handleDownload,
  }
}
