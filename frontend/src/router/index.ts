import type { RouteRecordRaw } from 'vue-router'
import {
  createRouter,
  createWebHistory,
} from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import ERouteNames from '@/router/route-names'

NProgress.configure({ showSpinner: false })

const ExternalChat = () => import('@/views/ExternalChat/index.vue')
const Login = () => import('@/views/Login/index.vue')
const Chat = () => import('@/views/Chat/index.vue')
const Application = () => import('@/views/Application/index.vue')
const AIDataset = () => import('@/views/AIDataset/index.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: {
      name: ERouteNames.LOGIN,
    },
  },
  {
    path: '/login',
    name: ERouteNames.LOGIN,
    component: Login,
    meta: {
      hideSidebar: true,
    },
  },
  {
    path: '/chat/:applicationId?',
    name: ERouteNames.CHAT,
    component: ExternalChat,
    meta: {
      hideSidebar: true,
      showHeader: false,
    },
  },
  {
    path: '/inner_chat/:applicationId?',
    name: ERouteNames.INNER_CHAT,
    component: Chat,
    meta: {
      hideSidebar: false,
      showHeader: true,
    },
  },
  {
    path: '/app',
    name: ERouteNames.APP,
    component: Application,
  },
  {
    path: '/ai-dataset',
    name: ERouteNames.AI_DATASET,
    component: AIDataset,
  },
]

const router = createRouter({
  history: createWebHistory(''),
  routes,
})

router.beforeEach((to, from, next) => {
  NProgress.start()
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
