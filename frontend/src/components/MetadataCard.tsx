export default function MetadataCard({ metadata }: { metadata: Record<string, unknown> }) {
  if (!metadata || Object.keys(metadata).length === 0) {
    return <p className="text-sm text-accent font-medium">No metadata available.</p>;
  }

  return (
    <div className="grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
      {Object.entries(metadata).map(([key, value]) => (
        <div key={key} className="flex flex-col border-b border-border/50 pb-2">
          <span className="text-xs uppercase tracking-widest font-bold text-accent mb-1">{key.replace(/_/g, ' ')}</span>
          <span className="font-mono text-foreground font-medium truncate" title={String(value)}>{String(value)}</span>
        </div>
      ))}
    </div>
  );
}
