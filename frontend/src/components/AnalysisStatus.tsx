export default function AnalysisStatus({ status }: { status: 'idle' | 'uploading' | 'processing' | 'error' | 'success' }) {
  if (status === 'idle') return null;

  return (
    <div className="flex flex-col items-center justify-center py-20 gap-5 bg-surface border border-border rounded-lg">
      {status === 'processing' && (
        <>
          <div className="relative w-10 h-10">
            <div className="absolute inset-0 rounded-full border-2 border-border" />
            <div className="absolute inset-0 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          </div>
          <div className="text-center">
            <p className="text-sm font-semibold text-foreground">Analyzing media&hellip;</p>
            <p className="text-sm text-muted mt-1">Running the existing classification pipeline. This may take a moment.</p>
          </div>
        </>
      )}
      {status === 'uploading' && (
        <>
          <div className="w-40 h-1 bg-border rounded-full overflow-hidden">
            <div className="h-full bg-primary animate-pulse w-full" />
          </div>
          <p className="text-sm text-muted">Uploading file&hellip;</p>
        </>
      )}
    </div>
  );
}
