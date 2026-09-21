export default function MetadataCard({ metadata }: { metadata: Record<string, unknown> }) {
  if (!metadata || Object.keys(metadata).length === 0) {
    return <p className="text-sm text-gray-500">No metadata available.</p>;
  }

  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
      {Object.entries(metadata).map(([key, value]) => (
        <div key={key} className="flex flex-col border-b border-border/50 pb-1">
          <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}</span>
          <span className="font-mono text-gray-200 truncate" title={String(value)}>{String(value)}</span>
        </div>
      ))}
    </div>
  );
}
