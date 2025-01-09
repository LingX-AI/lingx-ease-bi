import * as XLSX from 'xlsx'
import Papa from 'papaparse'
import { useClipboard, useScroll } from '@vueuse/core'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'

const { copy } = useClipboard()

/**
 * Modal Hook
 * @param title - Modal Title
 */
export const useModal = (
  title?: string,
) => {
  const visible = ref(false)
  const modelTitle = computed(() => {
    return title
  })
  const handleCancel = () => {
    visible.value = false
  }
  onMounted(() => {
    visible.value = true
  })
  return {
    visible,
    modelTitle,
    handleCancel,
  }
}

export const useScrollToBottom = () => {
  const warpRef = ref<HTMLElement | null>(null)
  const { y: scrollY, arrivedState } = useScroll(warpRef)
  const scrollToBottom = (smooth = false) => {
    nextTick(() => {
      const el = warpRef.value
      if (!el)
        return
      el.scrollTo({
        top: el.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto',
      })
    })
  }

  return {
    warpRef,
    scrollToBottom,
    scrollY,
    arrivedState,
  }
}

export const useExportChartData = () => {
  const exportExcel = (data: Record<string, any>[]) => {
    const worksheet = XLSX.utils.json_to_sheet(data)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1')
    XLSX.writeFile(workbook, 'data.xlsx')
  }

  const exportCsv = (data: Record<string, any>[]) => {
    const csv = Papa.unparse(data)
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    let link: any = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = 'data.csv'
    link.click()
    link = null
  }

  return {
    exportExcel,
    exportCsv,
  }
}

export const useCopy = () => {
  const { t } = useI18n()

  const handleCopy = async (text: string) => {
    await copy(text)
    message.success(t('common.copied'))
  }

  return {
    handleCopy,
  }
}
