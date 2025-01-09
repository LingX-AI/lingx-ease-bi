export interface IAnswer {
  chartOption?: string
  summary: string
  displayMode?: 'text' | 'table' | 'chart'
}

export enum EStepStatus {
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ERROR = 'error',
  CANCELLED = 'cancelled',
}

export enum EStepNames {
  QUESTION_AGENT = 'question_agent',
  SQL_GENERATOR_AGENT = 'sql_generator_agent',
  DB_QUERY_AGENT = 'db_query_agent',
  ANSWER_GENERATOR_AGENT = 'answer_generator_agent',
}

export interface IStep {
  id: string
  taskId: string
  step: EStepNames
  status: EStepStatus
  latency: number
  result: Record<string, any> | string[]
  answer?: IAnswer
  isFinalCompleted?: string
  sqlList?: string[]
  validSql?: string
  queryResult?: Record<string, any>[]
  stepTimes?: Record<string, number>
}

export interface IMessage {
  id?: string
  taskId?: string
  applicationId?: string | number
  question: string
  answer?: IAnswer
  queryResult?: Record<string, any>[]
  createdAt?: string
  isPendingResponse?: boolean
  isCancelled?: boolean
  isChartGenerating?: boolean
  checked?: boolean
  steps?: IStep[]
}
