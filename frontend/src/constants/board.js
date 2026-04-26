export const TTL_MIN = 1
export const TTL_MAX = 72

export const MAX_CUSTOM_COLUMNS = 4
export const MIN_CUSTOM_COLUMNS = 1

export const LIMITS = {
  TITLE: 100,
  DESCRIPTION: 500,
  CARD_TEXT: 500,
  COLUMN_NAME: 50,
  AUTHOR_NAME: 30,
}

export const STICKY_COLORS = ['yellow', 'pink', 'blue', 'green', 'purple']

export const STICKY_COLOR_CLASSES = {
  yellow: 'bg-yellow-100 border-yellow-200',
  pink: 'bg-pink-100 border-pink-200',
  blue: 'bg-blue-100 border-blue-200',
  green: 'bg-green-100 border-green-200',
  purple: 'bg-purple-100 border-purple-200',
}

export const STICKY_PICKER_CLASSES = {
  yellow: 'bg-yellow-200',
  pink: 'bg-pink-200',
  blue: 'bg-blue-200',
  green: 'bg-green-200',
  purple: 'bg-purple-200',
}

export const STORAGE_KEY_AUTHOR = 'hb_author'
export const STORAGE_KEY_ADMIN_PREFIX = 'hb_admin_'

export const WS_RECONNECT_BASE_MS = 1000
export const WS_RECONNECT_MAX_MS = 30000
export const WS_RECONNECT_MAX_RETRIES = 10
