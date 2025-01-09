import { nanoid } from 'nanoid'
import { getAuthTokenApi, getClientAccessTokenApi } from '@/services/apis/auth'
import { useUserStore } from '@/store'

export const useAuth = () => {
  const isInIframe = window.self !== window.top
  const store = useUserStore()
  const { setToken, setUserInfo } = store
  const { appUserId } = storeToRefs(store)
  const getAppUserId = () => {
    let appUserId = localStorage.getItem('appUserId')
    if (!appUserId) {
      appUserId = nanoid()
      localStorage.setItem('appUserId', appUserId)
    }
    return appUserId
  }
  const getClientAccessToken = async (applicationId: string) => {
    setToken('')
    const payload = { applicationId }
    const { code, data } = await getClientAccessTokenApi(payload)
    if (code === 0) {
      setToken(`Bearer ${data.accessToken}`)
    }
  }
  const getAuthToken = async () => {
    const _appUserId = appUserId.value || getAppUserId()
    const payload = {
      appUserId: _appUserId,
      email: `${_appUserId}@lingx.ai`,
    }
    const res = await getAuthTokenApi(payload)
    if (res?.code === 0) {
      setUserInfo({
        id: res?.data?.id,
      })
      setToken(`Bearer ${res?.data?.accessToken}`)
    }
  }

  const auth = async (applicationId: string) => {
    await getClientAccessToken(applicationId)
    await getAuthToken()
  }

  const handleListenAppUserIdChange = (event: MessageEvent) => {
    const appUserId = event.data?.appUserId
    appUserId && store.setAppUserId(appUserId)
  }

  const listenAppUserIdChange = () => {
    window.addEventListener('message', handleListenAppUserIdChange)

    onUnmounted(() => {
      window.removeEventListener('message', handleListenAppUserIdChange)
    })
  }

  return {
    isInIframe,
    auth,
    listenAppUserIdChange,
  }
}
