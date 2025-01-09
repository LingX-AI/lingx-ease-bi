import { createI18n } from 'vue-i18n'
import zh from './lang/zh'
import en from './lang/en'

type TLang = 'zh' | 'en'

const getLang = (): TLang => {
  const lang: unknown = localStorage.getItem('lang')
  if (['zh', 'en'].includes(lang as string))
    return lang as TLang
  const browserLanguage = navigator.language || (navigator as any).userLanguage || 'zh-CN'
  if (browserLanguage.startsWith('zh'))
    return 'zh'
  return 'en'
}

const i18n = createI18n({
  locale: getLang(),
  legacy: false,
  globalInjection: true,
  messages: {
    zh,
    en,
  },
})
export default i18n
