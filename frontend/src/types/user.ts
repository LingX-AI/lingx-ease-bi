export interface IUserInfo {
  id: string
  username: string
  avatar?: any
  email: string
  roles: Record<string, any>[]
  created_at: number
}
