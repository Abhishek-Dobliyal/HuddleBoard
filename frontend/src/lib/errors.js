export function getErrorMessage(err, fallback = 'Something went wrong') {
  const data = err?.response?.data
  if (!data) return fallback
  if (typeof data.detail === 'string') return data.detail
  if (Array.isArray(data.detail)) return data.detail.map((e) => e.msg).join('. ')
  if (Array.isArray(data)) return data.map((e) => e.msg).join('. ')
  return data.error || fallback
}
