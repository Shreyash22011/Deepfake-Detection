export default function SuspiciousFrames({ frames }: { frames: number[] }) {
  if (!frames || frames.length === 0) {
    return <p className="text-sm text-gray-500">No suspicious frames detected.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
        {frames.map((frame, idx) => (
          <div key={idx} className="flex-shrink-0 space-y-2">
            <div className="w-32 h-20 bg-background border border-danger/50 rounded-md flex items-center justify-center relative overflow-hidden group">
              <span className="text-xs text-gray-500">Frame {frame}</span>
              <div className="absolute inset-0 border border-danger opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </div>
            <p className="text-xs text-center font-mono text-danger">Time: {(frame / 30).toFixed(2)}s</p>
          </div>
        ))}
      </div>
    </div>
  );
}
