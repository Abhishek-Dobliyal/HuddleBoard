import { useToast } from './useToast'

export function useClipboard() {
  const { showToast } = useToast()

  async function copy(text, successMsg = 'Copied!') {
    try {
      await navigator.clipboard.writeText(text)
      showToast(successMsg, 'success')
    } catch {
      showToast('Failed to copy.', 'error')
    }
  }

  return { copy }
}
