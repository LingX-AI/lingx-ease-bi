import type { Emitter } from 'mitt'
import mitt from 'mitt'

export enum EEventNames {
  NEW_MESSAGE = 'new-message',
  MESSAGE_CANCELLED = 'message-cancelled',
  MESSAGE_DELETED = 'message-deleted',
}
type Events = Record<EEventNames, any>
export const emitter: Emitter<Events> = mitt<Events>()
