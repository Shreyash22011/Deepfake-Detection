import ResultHero from '@/components/ResultHero';
import SuspiciousFrames from '@/components/SuspiciousFrames';
import MediaPreview from '@/components/MediaPreview';
import HeatmapViewer from '@/components/HeatmapViewer';
import Link from 'next/link';

export default async function ResultPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params;
  const analysisId = resolvedParams.id;

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  let apiData = null;
  let fetchError = null;

  try {
    const res = await fetch(`${API_URL}/api/analyses/${analysisId}`, { cache: 'no-store' });
    if (!res.ok) {
      fetchError = 'Failed to load analysis. The record may not exist.';
    } else {
      apiData = await res.json();
    }
  } catch {
    fetchError = 'Network error. Is the backend running?';
  }

  // ── Error state
  if (fetchError) {
    return (
      <div className="max-w-7xl mx-auto px-5 sm:px-8 py-24 text-center">
        <p className="text-base font-semibold text-danger mb-2">Error loading result</p>
        <p className="text-sm text-muted mb-8">{fetchError}</p>
        <Link href="/analyze" className="text-sm font-medium text-primary hover:underline">
          Start a new analysis &rarr;
        </Link>
      </div>
    );
  }

  // ── Processing state
  if (apiData?.status === 'processing' || apiData?.status === 'pending') {
    return (
      <div className="max-w-7xl mx-auto px-5 sm:px-8 py-24 text-center">
        <div className="inline-flex items-center gap-3 mb-6">
          <div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <p className="text-sm font-medium text-foreground">Analysis in progress&hellip;</p>
        </div>
        <p className="text-sm text-muted">Please refresh this page in a moment.</p>
        <p className="text-xs text-muted font-mono mt-3">{analysisId}</p>
      </div>
    );
  }

  // ── Failed state
  if (apiData?.status === 'error') {
    return (
      <div className="max-w-7xl mx-auto px-5 sm:px-8 py-24 text-center">
        <p className="text-base font-semibold text-danger mb-2">Analysis Failed</p>
        <p className="text-sm text-muted mb-2">
          {apiData.error_message || 'An unknown error occurred during processing.'}
        </p>
        <p className="text-xs text-muted font-mono mb-8">{analysisId}</p>
        <Link href="/analyze" className="text-sm font-medium text-primary hover:underline">
          Try again &rarr;
        </Link>
      </div>
    );
  }

  // ── Success
  const result = apiData?.result || {};
  const prediction: string = result.prediction || 'uncertain';
  const confidence: number = result.confidence || 0;
  const modelName: string = result.model_name || 'Unknown';
  const mediaType: string = apiData?.media_type || 'video';
  const processingMs: number = result.processing_time_ms || 0;
  const filename: string = apiData?.filename || 'Unknown';
  const suspiciousFrames: number[] = result.evidence?.suspicious_frames || [];
  const fps: number = result.evidence?.video_metadata?.fps || 24;
  const note: string = result.evidence?.note || result.evidence?.error || '';

  return (
    <div className="max-w-7xl mx-auto px-5 sm:px-8 w-full py-8 pb-16">

      {/* ── Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8 pb-5 border-b border-border">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-muted mb-1">
            Analysis Result
          </p>
          <p className="text-xs font-mono text-muted">{analysisId}</p>
        </div>
        <div className="flex items-center gap-3">
          <button disabled title="Report export is not available in the current service" className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium border border-border text-muted rounded-md opacity-70 cursor-not-allowed">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
              <path fillRule="evenodd" d="M4.5 2A1.5 1.5 0 0 0 3 3.5v13A1.5 1.5 0 0 0 4.5 18h11a1.5 1.5 0 0 0 1.5-1.5V7.621a1.5 1.5 0 0 0-.44-1.06l-4.12-4.122A1.5 1.5 0 0 0 11.378 2H4.5Zm2.25 8.5a.75.75 0 0 0 0 1.5h6.5a.75.75 0 0 0 0-1.5h-6.5Zm0 3a.75.75 0 0 0 0 1.5h6.5a.75.75 0 0 0 0-1.5h-6.5Zm0-6a.75.75 0 0 0 0 1.5h6.5a.75.75 0 0 0 0-1.5h-6.5Z" clipRule="evenodd" />
            </svg>
            Export unavailable
          </button>
          <Link
            href="/analyze"
            className="inline-flex items-center px-4 py-2 text-xs font-semibold bg-primary text-white rounded-md hover:bg-primary-hover"
          >
            New Analysis
          </Link>
        </div>
      </div>

      {/* ── Main two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">

        {/* LEFT: Verdict + Details */}
        <div className="lg:col-span-2 space-y-6">

          {/* Verdict hero */}
          <ResultHero prediction={prediction} confidence={confidence} note={note} />

          {/* Analysis details */}
          <div className="bg-surface border border-border rounded-lg p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted mb-4">
              Analysis Details
            </p>
            <dl className="space-y-3">
              {[
                { label: 'Filename', value: filename },
                { label: 'Media type', value: mediaType.charAt(0).toUpperCase() + mediaType.slice(1) },
                { label: 'Model', value: modelName },
                { label: 'Processing time', value: `${processingMs.toLocaleString()} ms` },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between items-baseline gap-4 py-2.5 border-b border-border/60">
                  <dt className="text-xs font-medium text-muted flex-shrink-0">{label}</dt>
                  <dd className="text-sm text-foreground text-right font-mono truncate" title={value}>{value}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Heatmap */}
          <HeatmapViewer />

        </div>

        {/* RIGHT: Media + Evidence */}
        <div className="lg:col-span-3 space-y-6">

          {/* Media preview */}
          <div className="bg-surface border border-border rounded-lg p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted mb-3">
              Media Preview
            </p>
            <MediaPreview type={mediaType} analysisId={analysisId} />
          </div>

          {/* Flagged frames */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-muted mb-3">
              Flagged Evidence
            </p>
            {mediaType === 'video' ? (
              <SuspiciousFrames
                frames={suspiciousFrames}
                analysisId={analysisId}
                fps={fps}
              />
            ) : (
              <p className="text-sm text-muted">Frame evidence is only available for video analyses.</p>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
