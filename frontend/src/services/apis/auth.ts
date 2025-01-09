import type { AxiosResponse } from 'axios'
import request from '../request'

interface IParams {
  [prop: string]: any
}

interface IPayload extends IParams {
}

// 管理员登录
export const loginApi = async (payload: IPayload, config = {}) => {
  const res: AxiosResponse = await request.post('/admin/login/', payload, config)
  return res.data
}

// 获取客户端token
export const getClientAccessTokenApi = async (payload: { applicationId: string }, config = {}) => {
  const res: AxiosResponse = await request.post('/auth/client_token/', payload, config)
  return res.data
}

// 获取用户认证token
export const getAuthTokenApi = async (payload: IPayload = {}) => {
  const res: AxiosResponse = await request.post('/auth/chat_auth/', payload)
  return res.data
}
