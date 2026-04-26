/**
 * Extract a user-friendly error message from an API error.
 * Uses the server's detail message if available, otherwise falls back.
 */
export function getErrorMessage(err, fallback = 'Something went wrong') {
  return err?.response?.data?.detail || err?.response?.data?.error || fallback
}
