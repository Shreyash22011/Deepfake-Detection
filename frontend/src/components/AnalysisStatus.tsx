export default function AnalysisStatus({ status }: { status: 'idle' | 'uploading' | 'processing' | 'error' | 'success' }) {
  if (status === 'idle') return null;

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-panel border border-border rounded-xl space-y-4">
      {status === 'processing' && (
        <>
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 rounded-full border-4 border-primary/20"></div>
            <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
          </div>
          <p className="text-lg font-medium animate-pulse">Analyzing Media...</p>
          <p className="text-sm text-gray-400">Extracting forensic evidence</p>
        </>
      )}
      {status === 'uploading' && (
        <>
          <div className="w-full max-w-xs h-2 bg-background rounded-full overflow-hidden">
            <div className="h-full bg-primary animate-pulse w-full"></div>
          </div>
          <p className="font-medium text-sm">Uploading file...</p>
        </>
      )}
    </div>
  );
}
