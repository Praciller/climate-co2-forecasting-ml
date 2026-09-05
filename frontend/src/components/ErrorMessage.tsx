import { CircleAlert } from 'lucide-react'
import { Alert, AlertDescription } from './ui/alert'
import { Button } from './ui/button'

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <Alert
      className="mx-auto mt-16 max-w-xl border-destructive/40 bg-destructive/5 p-8 text-center"
    >
      <CircleAlert className="mx-auto text-danger" size={30} aria-hidden="true" />
      <h2 className="mt-4 text-xl font-medium">Forecasting API unavailable</h2>
      <AlertDescription className="mx-auto mt-2 max-w-md leading-6">{message} Start FastAPI on port 8000, then retry.</AlertDescription>
      {onRetry ? (
        <Button
          type="button"
          onClick={onRetry}
          className="mt-5"
        >
          Retry connection
        </Button>
      ) : null}
    </Alert>
  )
}
