import { CircleAlert } from 'lucide-react'

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <section
      className="mx-auto mt-16 max-w-xl rounded-xl border border-rule bg-surface p-8 text-center"
      role="alert"
    >
      <CircleAlert className="mx-auto text-danger" size={30} aria-hidden="true" />
      <h2 className="mt-4 text-xl font-semibold">Forecasting API unavailable</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-ink-muted">
        {message} Start FastAPI on port 8000, then retry.
      </p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-5 rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-opacity hover:opacity-90"
        >
          Retry connection
        </button>
      ) : null}
    </section>
  )
}
