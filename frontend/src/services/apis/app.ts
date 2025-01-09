import type { AxiosResponse } from 'axios'
import request from '../request'
import type { IAppPrompt, IAppTable, IModel, ITableColumn } from '@/types/app'

interface IParams {
  [prop: string]: any
}

interface IPayload extends IParams {
}

// 获取app/数据库列表
export const getAppDatabasesApi = async (payload: IPayload) => {
  const res: AxiosResponse = await request.get('/app', {
    params: payload,
  })
  return res.data
}

// 创建App
export const createAppApi = async (payload: IPayload) => {
  const res: AxiosResponse = await request.post('/app', payload)
  return res.data
}

// 更新App
export const updateAppApi = async (payload: IPayload) => {
  const res: AxiosResponse = await request.patch(`/app/${payload.id}`, payload)
  return res.data
}

// 获取某个App
export const getAppApi = async (applicationId: string | number) => {
  const res: AxiosResponse = await request.get(`/app/${applicationId}`)
  return res.data
}

// 获取App的数据库表
export const deleteAppApi = async (applicationId: number | string) => {
  const res: AxiosResponse = await request.delete(`/app/${applicationId}`)
  return res.data
}

// 创建App的数据表
export const createAppTablesApi = async (applicationId: number | string) => {
  const res: AxiosResponse = await request.post(`/app/${applicationId}/create_database_tables`)
  return res.data
}

// 获取App的数据库表
export const getAppTablesApi = async (applicationId: number | string) => {
  const res: AxiosResponse = await request.get('/app_table', {
    params: { application: applicationId },
  })
  return res.data
}

// 获取数据库表的字段
export const getAppTableColumnApi = async (tableId: string) => {
  const res: AxiosResponse = await request.get('/app_table_column', {
    params: { table: tableId },
  })
  return res.data
}

// 更新表
export const updateAppTableApi = async (tableId: string, payload: Partial<IAppTable>) => {
  const res: AxiosResponse = await request.patch(`/app_table/${tableId}`, { ...payload })
  return res.data
}

// 获取AI生成的表及字段的注释
export const getAppTableAICommentApi = async (tableId: string) => {
  const res: AxiosResponse = await request.get(`/app_table/${tableId}/get_ai_comment`)
  return res.data
}

// 更新字段
export const updateAppTableColumnApi = async (columnId: string, payload: Partial<ITableColumn>) => {
  const res: AxiosResponse = await request.patch(`/app_table_column/${columnId}`, { ...payload })
  return res.data
}

// 批量更新字段
export const batchUpdateAppTableColumnApi = async (payload: Partial<ITableColumn>[]) => {
  const res: AxiosResponse = await request.put('/app_table_column/batch_update', payload)
  return res.data
}

// 导出App的数据库表
export const appDatabaseSchemaApi = async (applicationId: string | number, type: 'json' | 'ddl') => {
  const res: AxiosResponse = await request.get(`/app/${applicationId}/export_database_schema`, {
    params: { type },
  })
  return res.data
}

// 启用/禁用检索
export const enableDisableRagApi = async (applicationId: string | number, isEnabled: boolean) => {
  const res: AxiosResponse = await request.put(`/app/${applicationId}/enable_disable_rag`, { isEnabled })
  return res.data
}

// 获取App数据的embedding文档
export const getAppDatabaseDocumentApi = async (applicationId: string | number) => {
  const res: AxiosResponse = await request.get('/app_document', {
    params: { application: applicationId },
  })
  return res.data
}

// 创建App数据的embedding文档
export const createAppDatabaseDocumentApi = async (applicationId: string | number) => {
  const res: AxiosResponse = await request.post('/app_document/create_embed', { applicationId })
  return res.data
}

// 检索文档
export const retrievalAppDatabaseDocumentApi = async (applicationId: string | number, text: string) => {
  const res: AxiosResponse = await request.post('/app_document/retrieval_embed', { applicationId, text })
  return res.data
}

// 获取App的微调示例
export const getAppFineTuningExamplesApi = async (payload: IPayload) => {
  const res: AxiosResponse = await request.get('/fine_tuning_example', {
    params: payload,
  })
  return res.data
}

// 创建微调用的问题示例
export const createFineTuningQuestionsApi = async (payload: {
  applicationId: string | number
  questionCount: number
}) => {
  const res: AxiosResponse = await request.post('/fine_tuning_example/create_questions', payload)
  return res.data
}

// 批量删除微调用的问题示例
export const batchDeleteFineTuningExampleApi = async (ids: string[]) => {
  const res: AxiosResponse = await request.post(`/fine_tuning_example/batch_delete`, { ids })
  return res.data
}

// 导出微调用的问题示例(非微调规范数据)
export const exportFineTuningExampleApi = async (applicationId: string | number, fileType: 'json' | 'csv' = 'json') => {
  const res: AxiosResponse = await request.get(`/fine_tuning_example/export_example`, {
    params: { applicationId, fileType },
    responseType: 'blob',
  })
  return res.data
}

// 获取微调用的问题示例(微调规范数据)
export const getStandardFineTuningExampleApi = async (applicationId: string | number) => {
  const res: AxiosResponse = await request.get(`/fine_tuning_example/get_standard_fine_tuning_example`, {
    params: { applicationId },
  })
  return res.data
}

// 微调参数配置
export const getFineTuningConfigApi = async (applicationId: string | number) => {
  const res: AxiosResponse = await request.get(`/fine_tuning_example/get_fine_tuning_config`, {
    params: { applicationId },
  })
  return res.data
}

// 获取微调WebUI的地址
export const getFineTuningWebUIUrlApi = async () => {
  const res: AxiosResponse = await request.get(`/fine_tuning_example/get_train_webui_url`)
  return res.data
}

// 获取提示词
export const getAppPromptApi = async (applicationId: number | string) => {
  const res: AxiosResponse = await request.get('/app_prompt/get_prompt', {
    params: { applicationId },
  })
  return res.data
}

// 更新提示词
export const updateAppPromptApi = async (payload: IAppPrompt) => {
  const res: AxiosResponse = await request.put('/app_prompt/update_prompt', payload)
  return res.data
}

// 生成sql
export const createSqlApi = async (payload: {
  applicationId: string | number
  question: string
}) => {
  const res: AxiosResponse = await request.post('/fine_tuning_example/create_sql', payload)
  return res.data
}

// 执行sql
export const executeSqlApi = async (payload: {
  applicationId: string | number
  question: string
  sql: string
}) => {
  const res: AxiosResponse = await request.post('/fine_tuning_example/execute_sql', payload)
  return res.data
}

// 保存sql
export const saveSqlApi = async (payload: {
  application: string | number
  question: string
  sql: string
}) => {
  const res: AxiosResponse = await request.post('/fine_tuning_example', payload)
  return res.data
}

// 获取部署的模型
export const getModelsApi = async (applicationId: number | string) => {
  const res: AxiosResponse = await request.get('/fine_tuning_model', {
    params: { application: applicationId },
  })
  return res.data
}

// 转换模型
export const convertModelApi = async (payload: Record<string, any>) => {
  const res: AxiosResponse = await request.post('/convert_model', payload)
  return res.data
}

// 部署模型
export const deploymentModelApi = async (payload: Record<string, any>) => {
  const res: AxiosResponse = await request.post('/deployment_model', payload)
  return res.data
}

// 更新部署模型
export const updateModelApi = async (id: string, payload: Partial<IModel>) => {
  const res: AxiosResponse = await request.patch(`/fine_tuning_model/${id}`, payload)
  return res.data
}

// 启用/禁用部署模型
export const enableDisableModelApi = async (id: string, isEnabled: boolean) => {
  const res: AxiosResponse = await request.put(`/fine_tuning_model/${id}/enable_disable_model`, { isEnabled })
  return res.data
}

// 删除部署模型
export const deleteModelApi = async (id: string) => {
  const res: AxiosResponse = await request.delete(`/fine_tuning_model/${id}`)
  return res.data
}

// 获取用户认证token
export const getAuthTokenApi = async (payload: IPayload = {}) => {
  const res: AxiosResponse = await request.post('/auth/chat_auth/', payload)
  return res.data
}

// 获取建议问题列表
export const getSuggestedQuestionsApi = async (applicationId: string | number) => {
  const res: AxiosResponse = await request.get('/application-suggested-questions', {
    params: { application: applicationId },
  })
  return res.data
}

// 批量更新建议问题
export const batchUpdateSuggestedQuestionsApi = async (applicationId: string | number, questions: string[]) => {
  const res: AxiosResponse = await request.post('/application-suggested-questions/batch_update', {
    applicationId,
    questions,
  })
  return res.data
}
