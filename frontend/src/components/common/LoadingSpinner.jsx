import clsx from 'clsx'

export default function LoadingSpinner({ fullScreen = false, size = 'md', className }) {
  const sizes = { sm: 'h-5 w-5', md: 'h-8 w-8', lg: 'h-12 w-12' }

  const spinner = (
    <div className={clsx(
      'animate-spin rounded-full border-4 border-primary-200 border-t-primary-600',
      sizes[size],
      className
    )} />
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white/80 z-50">
        <div className="flex flex-col items-center gap-4">
          {spinner}
          <p className="text-primary-600 font-medium animate-pulse">Loading...</p>
        </div>
      </div>
    )
  }

  return spinner
}
