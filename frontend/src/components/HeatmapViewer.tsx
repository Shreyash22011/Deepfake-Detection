export default function HeatmapViewer({ regions }: { regions: number[][] }) {
  if (!regions || regions.length === 0) {
    return <p className="text-sm text-gray-500">No suspicious regions detected.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="aspect-video bg-background rounded-lg border border-border relative overflow-hidden flex items-center justify-center">
        <p className="text-gray-500 text-sm z-10">Image Preview (Mock)</p>
        {/* Mock heatmap overlay */}
        <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-danger/20 to-transparent mix-blend-overlay"></div>
        
        {/* Render mock bounding boxes */}
        {regions.map((region, idx) => (
          <div 
            key={idx}
            className="absolute border-2 border-danger shadow-[0_0_15px_rgba(239,68,68,0.5)]"
            style={{
              left: `${region[0]}%`,
              top: `${region[1]}%`,
              width: `${region[2] - region[0]}%`,
              height: `${region[3] - region[1]}%`,
            }}
          />
        ))}
      </div>
      <p className="text-xs text-gray-400">Heatmap indicates areas of high model activation (e.g., Grad-CAM).</p>
    </div>
  );
}
