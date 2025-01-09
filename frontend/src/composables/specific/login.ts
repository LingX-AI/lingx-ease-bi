import { loginApi } from '@/services/apis/auth'
import { useUserStore } from '@/store'
import ERouteNames from '@/router/route-names'

export const useLogin = () => {
  const store = useUserStore()
  const router = useRouter()
  const login = async (email: string, password: string, remember = true) => {
    const res = await loginApi({
      email,
      password,
    })
    if (res?.code === 0) {
      const { access, id, username, email } = res.data
      store.setToken(`Bearer ${access}`)
      store.setUserInfo({ id, username, email })
      router.replace({
        name: ERouteNames.INNER_CHAT,
      }).then(() => {
        if (remember) {
          localStorage.setItem('username', email)
        }
      })
    }
  }

  return {
    login,
  }
}
