export interface IAppDatabase {
  id: number
  createdAt: string
  updatedAt: string
  clientId: string
  client_type: string
  authorizationGrantType: string
  clientSecret: string
  hash_client_secret: boolean
  name: string
  skipAuthorization: boolean
  created: string
  updated: string
  algorithm: string
  allowedOrigins: string
  isEnabled: boolean
  isDeleted: boolean
  description: string
  databaseConfiguration?: any
  user: string
}

export interface ITableColumn {
  id: string
  key: string
  name: string
  type: string
  comment: string
  aiComment: string
  originalAiComment: string
  default: any
  nullable: string
  isEnabled: boolean
}

export interface IAppTable {
  id: string
  name: string
  table?: string
  columns?: ITableColumn[]
  comment: string
  aiComment: string
  isEnabled: boolean
}

export interface IAppFineTuningExample {
  application?: IAppDatabase
  question: string
  sql: string
  result?: Record<string, any>[]
  createdAt: string
}

export interface IStandardFineTuningExample {
  instruction: string
  input: string
  output: string
}

export interface IAppPrompt {
  applicationId: string | number
  questionCleanPrompt?: string
  columnCommentPrompt?: string
  questionBuilderPrompt?: string
  schemaRagPrompt?: string
  sqlGeneratorPrompt?: string
}

export interface IDatabaseDocument {
  id: string
  documentName: string
  documentPath: string
  documentSize: string
  contentType: string
  token_count?: number
  character_count?: number
}

export interface IModel {
  id?: string
  modelName: string
  description?: string
  isEnabled: boolean
}

export interface IAppSuggestedQuestion {
  id?: number
  applicationId: number
  question: string
  displayOrder?: number
  createdAt?: string
  updatedAt?: string
}
