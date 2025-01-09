import { createPinia, defineStore } from 'pinia'
import type { IUserInfo } from '@/types/user'
import ERouteNames from '@/router/route-names'

export const useUserStore = defineStore(
  'user',
  () => {
    const router = useRouter()
    const token = ref<string>('')
    const userInfo = ref<Partial<IUserInfo>>({
      id: '',
    })
    const appUserId = ref('')
    // 设置请求token
    const setToken = (_token: string) => {
      token.value = _token
    }
    // 设置当前登录用户信息
    const setUserInfo = (_userInfo: any = {}) => {
      userInfo.value = _userInfo
    }

    const setAppUserId = (_appUserId: string) => {
      appUserId.value = _appUserId
    }

    const clear = () => {
      setToken('')
      setUserInfo({})
    }

    const logout = () => {
      clear()
      router.replace({
        name: ERouteNames.LOGIN,
      })
    }

    return {
      token,
      userInfo,
      appUserId,
      setAppUserId,
      setToken,
      setUserInfo,
      clear,
      logout,
    }
  },
  {
    persist: {
      paths: ['token', 'userInfo'],
    },
  },
)

const store = createPinia()
export default store
