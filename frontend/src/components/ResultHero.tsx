interface ResultHeroProps {
  prediction: string;
  confidence: number;
  note?: string;
}

export default function ResultHero({ prediction, confidence, note }: ResultHeroProps) {
  const pred = prediction.toLowerCase();
  const isFake = pred === 'fake' || pred === 'synthetic';
  const isReal = pred === 'real';

  const semanticColor = isFake
    ? 'text-danger'
    : isReal
    ? 'text-success'
    : 'text-warning';

  const semanticBg = isFake
    ? 'bg-danger/8 border-danger/20'
    : isReal
    ? 'bg-success/8 border-success/20'
    : 'bg-warning/8 border-warning/20';

  const confidencePct = (confidence * 100).toFixed(1);

  const defaultNote = isFake
    ? 'High probability of AI manipulation detected in this media.'
    : isReal
    ? 'No significant signs of AI manipulation were detected.'
    : 'Analysis result is inconclusive. Manual review recommended.';

  return (
    <div className="space-y-5">
      {/* Status badge */}
      <div className={`inline-flex items-center gap-2 px-3 py-1.5 border text-xs font-semibold rounded-sm ${semanticBg} ${semanticColor}`}>
        <span className={`w-1.5 h-1.5 rounded-full bg-current`} />
        {isFake ? 'Manipulation Detected' : isReal ? 'Authentic Media' : 'Inconclusive'}
      </div>

      {/* Prediction */}
      <div>
        <p className={`text-4xl font-bold tracking-tight leading-none ${semanticColor}`}>
          {prediction.toUpperCase()}
        </p>
        <div className="flex items-baseline gap-2 mt-3">
          <span className="text-3xl font-bold text-foreground">{confidencePct}%</span>
          <span className="text-sm text-muted">confidence</span>
        </div>
      </div>

      {/* Confidence bar */}
      <div className="space-y-1.5">
        <div className="h-1.5 bg-border rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${
              isFake ? 'bg-danger' : isReal ? 'bg-success' : 'bg-warning'
            }`}
            style={{ width: `${confidencePct}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-muted font-medium">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Note */}
      <p className="text-sm text-accent leading-relaxed">
        {note || defaultNote}
      </p>
    </div>
  );
}
