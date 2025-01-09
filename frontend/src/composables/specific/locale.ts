export const useExternalLocale = () => {
  const { locale } = useI18n()
  const handleExternalLocaleChange = (event: MessageEvent) => {
    const message = event.data
    const _locale = message.locale
    if (['zh', 'en'].includes(_locale)) {
      locale.value = _locale
    }
  }
  window.addEventListener('message', handleExternalLocaleChange)

  onUnmounted(() => {
    window.removeEventListener('message', handleExternalLocaleChange)
  })
}
