import { cloneDeep } from 'lodash-es'
import { message, notification } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import { jsonObj2JsonFile } from '@/utils/common'
import type {
  IAppDatabase,
  IAppFineTuningExample,
  IAppPrompt,
  IAppSuggestedQuestion,
  IAppTable,
  IDatabaseDocument,
  IModel,
  IStandardFineTuningExample,
  ITableColumn,
} from '@/types/app'
import {
  appDatabaseSchemaApi,
  batchDeleteFineTuningExampleApi,
  batchUpdateAppTableColumnApi,
  batchUpdateSuggestedQuestionsApi,
  convertModelApi,
  createAppApi,
  createAppDatabaseDocumentApi,
  createAppTablesApi,
  createFineTuningQuestionsApi,
  createSqlApi,
  deleteAppApi,
  deleteModelApi,
  deploymentModelApi,
  enableDisableModelApi,
  enableDisableRagApi,
  executeSqlApi,
  exportFineTuningExampleApi,
  getAppApi,
  getAppDatabaseDocumentApi,
  getAppDatabasesApi,
  getAppFineTuningExamplesApi,
  getAppPromptApi,
  getAppTableAICommentApi,
  getAppTableColumnApi,
  getAppTablesApi,
  getFineTuningConfigApi,
  getFineTuningWebUIUrlApi,
  getModelsApi,
  getStandardFineTuningExampleApi,
  getSuggestedQuestionsApi,
  retrievalAppDatabaseDocumentApi,
  saveSqlApi,
  updateAppApi,
  updateAppPromptApi,
  updateAppTableApi,
  updateAppTableColumnApi,
  updateModelApi,
} from '@/services/apis/app'

export const useAppDatabase = () => {
  const application = ref<IAppDatabase>()
  const appDatabases = ref<IAppDatabase[]>([])
  const suggestedQuestions = ref<IAppSuggestedQuestion[]>([])

  const getAppDatabases = async () => {
    const { code, data } = await getAppDatabasesApi({ page: 1, pageSize: 10 })
    if (code === 0) {
      appDatabases.value = data ?? []
    }
  }

  const createApplication = async (payload: Parameters<typeof createAppApi>[0]) => {
    const { code, data } = await createAppApi(payload)
    if (code === 0) {
      application.value = data
      return data
    }
  }

  const updateApplication = async (payload: Parameters<typeof updateAppApi>[0]) => {
    const { code, data } = await updateAppApi(payload)
    if (code === 0) {
      application.value = data
      return data
    }
  }

  const deleteApplication = async (applicationId: string | number) => {
    const { code } = await deleteAppApi(applicationId)
    if (code === 0) {
      const chatApplicationId = localStorage.getItem('chatApplicationId')
      if (chatApplicationId === `${applicationId}`) {
        localStorage.removeItem('chatApplicationId')
      }
      return true
    }
  }

  const getApplication = async (applicationId: string | number) => {
    const { code, data } = await getAppApi(applicationId)
    if (code === 0) {
      application.value = data
      return data
    }
  }

  const enableDisableRag = async (applicationId: string | number, isEnabled: boolean) => {
    await enableDisableRagApi(applicationId, isEnabled)
  }

  const getSuggestedQuestions = async (applicationId: string | number) => {
    const { code, data } = await getSuggestedQuestionsApi(applicationId)
    if (code === 0) {
      suggestedQuestions.value = data
      return data
    }
  }

  const updateSuggestedQuestions = async (applicationId: string | number, questions: string[]) => {
    const { code } = await batchUpdateSuggestedQuestionsApi(applicationId, questions)
    if (code === 0) {
      return true
    }
    return false
  }

  return {
    appDatabases,
    getAppDatabases,
    application,
    createApp,
    createApplication,
    updateApplication,
    getApplication,
    deleteApplication,
    enableDisableRag,
    suggestedQuestions,
    getSuggestedQuestions,
    updateSuggestedQuestions,
  }
}

export const useDataStructure = () => {
  const { t } = useI18n()
  const dataStructureTree = ref<IAppTable[]>([])
  let dataStructureTreeCache: IAppTable[] = []
  const tableColumns = ref<ITableColumn[]>([])
  const appDatabaseSchema = ref<IAppTable[]>([])
  const databaseDocument = ref<IDatabaseDocument[]>([])
  const loadingCreateDataStructure = ref(false)
  const loadingGetDataStructure = ref(false)
  const loadingGetTableColumns = ref(false)
  const loadingGetAppTableAIComment = ref(false)
  const loadingCreateAppDatabaseDocument = ref(false)

  const _formatDataStructureTree = (data: IAppTable[]) => {
    data.forEach((table: IAppTable & Record<string, any>) => {
      table.title = table.name
      table.key = table.id
    })
    data.sort((a, b) => Number(b.isEnabled) - Number(a.isEnabled))
    dataStructureTree.value = data
    dataStructureTreeCache = cloneDeep(dataStructureTree.value)
  }

  const getDataStructure = async (applicationId: number) => {
    loadingGetDataStructure.value = true
    const { code, data } = await getAppTablesApi(applicationId).finally(() => {
      loadingGetDataStructure.value = false
    })
    if (code === 0) {
      _formatDataStructureTree(data)
    }
  }

  const createDataStructure = async (applicationId: number | string) => {
    loadingCreateDataStructure.value = true
    const { code, data } = await createAppTablesApi(applicationId).finally(() => {
      loadingCreateDataStructure.value = false
    })
    if (code === 0) {
      _formatDataStructureTree(data)
    }
  }

  const getAppTableColumns = async (tableId: string) => {
    loadingGetTableColumns.value = false
    const { code, data } = await getAppTableColumnApi(tableId).finally(() => {
      loadingGetTableColumns.value = false
    })
    if (code === 0) {
      data.sort((a: ITableColumn, b: ITableColumn) => Number(b.isEnabled) - Number(a.isEnabled))
      tableColumns.value = data
    }
  }

  const getAppTableAIComment = async (tableId: string) => {
    loadingGetAppTableAIComment.value = true
    const { code, data } = await getAppTableAICommentApi(tableId).finally(() => {
      loadingGetAppTableAIComment.value = false
    })
    if (code === 0) {
      return data
    }
  }

  const updateAppTable = async (tableId: string, payload: Partial<IAppTable>) => {
    await updateAppTableApi(tableId, payload)
  }

  const updateAppTableColumn = async (columnId: string, payload: Partial<ITableColumn>) => {
    await updateAppTableColumnApi(columnId, payload)
  }

  const batchUpdateAppTableColumn = async (payload: Parameters<typeof batchUpdateAppTableColumnApi>[0]) => {
    await batchUpdateAppTableColumnApi(payload)
    message.success(t('common.saveSuccess'))
  }

  const getAppDatabaseSchema = async (applicationId: string | number, type: 'json' | 'ddl' = 'json') => {
    const { code, data } = await appDatabaseSchemaApi(applicationId, type)
    if (code === 0) {
      appDatabaseSchema.value = data ?? []
    }
  }

  const exportAppDatabaseSchema = async (applicationId: string | number, type: 'json' | 'ddl' = 'json') => {
    const { code, data } = await appDatabaseSchemaApi(applicationId, type)
    if (code === 0) {
      const fileName = `database_schema_${type}.json`
      jsonObj2JsonFile(data, fileName)
    }
  }

  return {
    loadingCreateDataStructure,
    loadingGetDataStructure,
    loadingGetTableColumns,
    loadingGetAppTableAIComment,
    loadingCreateAppDatabaseDocument,
    dataStructureTree,
    getAppTableAIComment,
    dataStructureTreeCache,
    appDatabaseSchema,
    tableColumns,
    databaseDocument,
    getDataStructure,
    createDataStructure,
    getAppTableColumns,
    updateAppTable,
    batchUpdateAppTableColumn,
    updateAppTableColumn,
    exportAppDatabaseSchema,
    getAppDatabaseSchema,
  }
}

export const useFineTuningExample = (applicationId: string | number = '') => {
  const { t } = useI18n()
  const fineTuningExamples = ref<IAppFineTuningExample[]>([])
  const standardFineTuningExamples = ref<IStandardFineTuningExample[]>([])
  const fineTuningConfig: Record<string, any> = ref({})
  const loadingFineTuningExample = ref(false)
  const loadingExportFineTuningExample = ref(false)
  const loadingCreateFineTuningQuestions = ref(false)
  const loadingCreateSql = ref(false)
  const loadingExecuteSql = ref(false)
  const pagination = ref({
    total: 0,
    current: 1,
    defaultPageSize: 30,
    pageSize: 30,
    showSizeChanger: true,
    size: 'small',
    showTotal(total: number) {
      return `${t('common.total')}: ${total}`
    },
    onChange(page: number, pageSize: number) {
      pagination.value.current = page
      pagination.value.pageSize = pageSize
      getFineTuningExamples({ applicationId })
    },
  })
  const questions = ref<IAppFineTuningExample[]>([])

  const getFineTuningExamples = async (payload: Record<string, any>) => {
    loadingFineTuningExample.value = false
    const _payload = { ...payload, page: pagination.value.current, pageSize: pagination.value.pageSize }
    const { code, data } = await getAppFineTuningExamplesApi(_payload).finally(() => {
      loadingFineTuningExample.value = false
    })
    if (code === 0) {
      fineTuningExamples.value = data?.results ?? []
      pagination.value = { ...pagination.value, total: data?.count ?? 0 }
    }
  }

  const createFineTuningQuestions = async (payload: Parameters<typeof createFineTuningQuestionsApi>[0]) => {
    loadingCreateFineTuningQuestions.value = true
    const { code, data } = await createFineTuningQuestionsApi(payload).finally(() => {
      loadingCreateFineTuningQuestions.value = false
    })
    if (code === 0) {
      questions.value = data.map((item: string) => {
        return {
          applicationId: payload.applicationId,
          question: item,
          sql: '',
          result: [],
        }
      })
    }
  }

  const createSql = async (payload: Parameters<typeof createSqlApi>[0]) => {
    loadingCreateSql.value = true
    const { code, data } = await createSqlApi(payload).finally(() => {
      loadingCreateSql.value = false
    })
    if (code === 0) {
      return data?.sql
    }
  }

  const executeSql = async (payload: Parameters<typeof executeSqlApi>[0]) => {
    loadingExecuteSql.value = true
    const { code, data } = await executeSqlApi(payload).finally(() => {
      loadingExecuteSql.value = false
    })
    if (code === 0) {
      return data
    }
  }

  const saveSql = async (payload: Parameters<typeof saveSqlApi>[0]) => {
    const { code } = await saveSqlApi(payload)
    if (code === 0) {
      message.success(t('dataset.fineTuningExample.saveSuccess'))
      return true
    }
    return false
  }

  const deleteFineTuningExample = async (ids: Parameters<typeof batchDeleteFineTuningExampleApi>[0]) => {
    if (!ids.length) {
      message.warning(t('dataset.fineTuningExample.noQuestions'))
      return
    }
    const { code } = await batchDeleteFineTuningExampleApi(ids)
    if (code === 0) {
      message.success(t('common.deleteSuccess'))
      await getFineTuningExamples({ applicationId })
    }
  }

  const exportFineTuningExample = async (applicationId: string | number, fileType: 'json' | 'csv') => {
    loadingExportFineTuningExample.value = true
    const data = await exportFineTuningExampleApi(applicationId, fileType).finally(() => {
      loadingExportFineTuningExample.value = false
    })
    let a: any = document.createElement('a')
    a.href = URL.createObjectURL(data)
    a.download = `fine-tuning-examples.${fileType}`
    a.click()
    URL.revokeObjectURL(a.href)
    a = null
  }

  const getStandardFineTuningExample = async (applicationId: string | number) => {
    const { code, data } = await getStandardFineTuningExampleApi(applicationId)
    if (code === 0) {
      standardFineTuningExamples.value = data
    }
  }

  const getFineTuningConfig = async (applicationId: string | number) => {
    const { code, data } = await getFineTuningConfigApi(applicationId)
    if (code === 0) {
      fineTuningConfig.value = data
    }
  }

  const openFineTuningWebUI = async () => {
    const { code, data } = await getFineTuningWebUIUrlApi()
    if (code === 0) {
      return data
    }
  }

  return {
    loadingFineTuningExample,
    loadingCreateFineTuningQuestions,
    loadingExportFineTuningExample,
    loadingCreateSql,
    loadingExecuteSql,
    fineTuningExamples,
    getFineTuningExamples,
    pagination,
    questions,
    createFineTuningQuestions,
    createSql,
    executeSql,
    saveSql,
    deleteFineTuningExample,
    exportFineTuningExample,
    getStandardFineTuningExample,
    standardFineTuningExamples,
    fineTuningConfig,
    getFineTuningConfig,
    openFineTuningWebUI,
  }
}

export const usePrompt = () => {
  const { t } = useI18n()
  const appPrompt = reactive<IAppPrompt>({
    applicationId: '',
    questionCleanPrompt: '',
    columnCommentPrompt: '',
    questionBuilderPrompt: '',
    schemaRagPrompt: '',
    sqlGeneratorPrompt: '',
  })

  const getAppPrompt = async (applicationId: string | number) => {
    const { code, data } = await getAppPromptApi(applicationId)
    if (code === 0) {
      Object.keys(appPrompt).forEach((key) => {
        (appPrompt as any)[key] = data[key]
      })
    }
  }
  const updateAppPrompt = async (payload: Parameters<typeof updateAppPromptApi>[0]) => {
    const { code } = await updateAppPromptApi(payload)
    if (code === 0) {
      message.success(t('dataset.promptWord.updateSuccess'))
    }
  }

  return {
    appPrompt,
    getAppPrompt,
    updateAppPrompt,
  }
}

export const useEmbedding = () => {
  const { t } = useI18n()
  const databaseDocuments = ref<IDatabaseDocument[]>([])
  const retrievedDocuments = ref<{ content: string, similarity: number }[]>([])
  const loadingCreateAppDatabaseDocument = ref(false)
  const loadingRetrievalAppDatabaseDocument = ref(false)
  const retrievalTime = ref(0)
  const getAppDatabaseDocument = async (applicationId: string | number) => {
    loadingRetrievalAppDatabaseDocument.value = true
    const { code, data } = await getAppDatabaseDocumentApi(applicationId).finally(() => {
      loadingRetrievalAppDatabaseDocument.value = false
    })
    if (code === 0) {
      databaseDocuments.value = data
    }
  }

  const retrievalAppDatabaseDocument = async (applicationId: string | number, text: string) => {
    if (!text.trim()) {
      return
    }
    const { code, data } = await retrievalAppDatabaseDocumentApi(applicationId, text)
    if (code === 0) {
      retrievedDocuments.value = data?.contents
      retrievalTime.value = data?.totalTime
    }
  }

  const createAppDatabaseDocument = async (applicationId: string | number) => {
    loadingCreateAppDatabaseDocument.value = true
    const { code, data } = await createAppDatabaseDocumentApi(applicationId).finally(() => {
      loadingCreateAppDatabaseDocument.value = false
    })
    if (code === 0) {
      message.success(t('dataset.embeddingDocument.createSuccess'))
      databaseDocuments.value = data
    }
  }
  return {
    databaseDocuments,
    retrievedDocuments,
    retrievalTime,
    loadingCreateAppDatabaseDocument,
    loadingRetrievalAppDatabaseDocument,
    getAppDatabaseDocument,
    retrievalAppDatabaseDocument,
    createAppDatabaseDocument,
  }
}

export const useDeploymentModel = () => {
  const { t } = useI18n()
  const models = ref<IModel[]>([])
  const getModels = async (applicationId: string | number) => {
    const { code, data } = await getModelsApi(applicationId)
    if (code === 0) {
      models.value = data
    }
  }

  const convertModel = async (payload: Record<string, any>) => {
    const { code } = await convertModelApi(payload)
    if (code === 0) {
      notification.success({
        message: t('dataset.deploymentModel.convertSuccess'),
        duration: null,
      })
    }
  }

  const deploymentModel = async (payload: Record<string, any>) => {
    const { code } = await deploymentModelApi(payload)
    if (code === 0) {
      notification.success({
        message: t('dataset.deploymentModel.deploySuccess'),
        duration: null,
      })
    }
  }

  const updateModel = async (modelId: string, payload: Partial<IModel>) => {
    const { code, data } = await updateModelApi(modelId, payload)
    if (code === 0) {
      return data
    }
  }

  const enableDisableModel = async (modelId: string, isEnabled: boolean) => {
    const { code } = await enableDisableModelApi(modelId, isEnabled)
    if (code === 0) {
      message.success(isEnabled ? t('common.enableSuccess') : t('common.disableSuccess'))
    }
  }

  const deleteModel = async (modelId: string) => {
    const { code, data } = await deleteModelApi(modelId)
    if (code === 0) {
      return data
    }
  }

  return {
    models,
    getModels,
    convertModel,
    deploymentModel,
    updateModel,
    deleteModel,
    enableDisableModel,
  }
}
