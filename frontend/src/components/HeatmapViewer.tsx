export default function HeatmapViewer() {
  return (
    <div className="bg-surface border border-border rounded-lg p-5">
      <p className="text-xs font-semibold uppercase tracking-widest text-muted mb-4">
        Visual Explainability
      </p>
      <div className="px-0 py-2">
        <p className="text-sm font-medium text-foreground mb-1">Visual explainability unavailable</p>
        <p className="text-xs text-muted leading-relaxed">
          Visual explainability is unavailable for this model version.
        </p>
      </div>
    </div>
  );
}
