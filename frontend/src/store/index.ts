import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

export { useUserStore } from './modules/user'

const store = createPinia()
store.use(piniaPluginPersistedstate)
export default store
