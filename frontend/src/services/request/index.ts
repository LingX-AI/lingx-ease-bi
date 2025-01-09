import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import axios from 'axios'
import { message as showMessage } from 'ant-design-vue'
import { useUserStore } from '@/store'

interface Result<T> {
  code: number
  message?: string
  msg?: string
  result: T
}

const HttpStatusMessages: { [key: number | string]: string } = {
  400: 'Request parameter error.',
  401: 'Unauthenticated or your certification has expired, please log in again.',
  403: 'Unauthorized access.',
  404: 'Request address error.',
  408: 'Request timeout.',
  500: 'Server exception.',
  501: 'Service not implemented.',
  502: 'Network exception.',
  503: 'Service unavailable.',
  504: 'Network timeout.',
  default: 'Request exception, please try again later.',
}

class Request {
  instance: AxiosInstance
  baseConfig: AxiosRequestConfig = {
    baseURL: import.meta.env.VITE_API_ENDPOINT,
    timeout: 5 * 60 * 1000,
  }

  constructor(config: AxiosRequestConfig = {}) {
    this.instance = axios.create({ ...this.baseConfig, ...config })

    this.instance.interceptors.request.use(this.handleRequest, this.handleError)
    this.instance.interceptors.response.use(this.handleResponse, this.handleResponseError)
  }

  private handleRequest(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
    const store = useUserStore()
    if (store.token) {
      (config.headers as any).Authorization = store.token
    }
    return config
  }

  private handleResponse(response: AxiosResponse): AxiosResponse {
    if (response.data?.code === 1) {
      const message = response.data?.msg || response.data?.message || HttpStatusMessages.default
      showMessage.error(message)
    }
    return response
  }

  private handleResponseError(error: any): Promise<any> {
    const status = error?.response?.status
    const message = HttpStatusMessages[status] || HttpStatusMessages.default
    showMessage.error(message)
    return Promise.reject(error.response)
  }

  private handleError(error: any): Promise<any> {
    return Promise.reject(error)
  }

  request<T = any>(config: AxiosRequestConfig): Promise<AxiosResponse<Result<T>>> {
    return this.instance.request(config)
  }

  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<Result<T>>> {
    return this.instance.get(url, config)
  }

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<Result<T>>> {
    return this.instance.post(url, data, config)
  }

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<Result<T>>> {
    return this.instance.put(url, data, config)
  }

  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<Result<T>>> {
    return this.instance.patch(url, data, config)
  }

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<Result<T>>> {
    return this.instance.delete(url, config)
  }
}

export default new Request()
