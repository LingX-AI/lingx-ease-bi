import type { AxiosResponse } from 'axios'
import request from '../request'

interface IParams {
  [prop: string]: any
}

interface IPayload extends IParams {
}

// 获取对话消息列表
export const getMyMessagesApi = async (params: IParams = {}) => {
  const res: AxiosResponse = await request.get('/message', {
    params,
  })
  return res.data
}

// 获取某条消息
export const getMessageApi = async (id: string) => {
  const res: AxiosResponse = await request.get(`/message/${id}`)
  return res.data
}

// 删除某条消息
export const deleteMessageApi = async (id: string) => {
  const res: AxiosResponse = await request.delete(`/message/${id}`)
  return res.data
}

// 批量删除消息
export const batchDeleteMessageApi = async (ids: string[]) => {
  const res: AxiosResponse = await request.post('/message/batch_delete', { ids })
  return res.data
}

// 聊天
export const chatApi = async (payload: IPayload = {}) => {
  const res: AxiosResponse = await request.post('/chat', payload)
  return res.data
}

// 取消聊天
export const cancelChatApi = async (payload: IPayload = {}) => {
  const res: AxiosResponse = await request.post('/cancel_chat', payload)
  return res.data
}

// 生成图表
export const generateChartOptionApi = async (payload: IPayload = {}) => {
  const res: AxiosResponse | void = await request.post('/generate_chart', payload).catch(() => {
  })
  return res?.data
}
