export default function ConfidenceMeter({ confidence, prediction = '' }: { confidence: number, prediction?: string }) {
  const percentage = Math.round(confidence * 100);

  let color = 'bg-warning'; // Default uncertain
  const predLower = prediction.toLowerCase();

  if (predLower === 'real') {
    color = 'bg-success';
  } else if (predLower === 'fake' || predLower === 'synthetic') {
    color = 'bg-danger';
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center text-sm">
        <span className="text-xs uppercase tracking-widest font-bold text-accent">Confidence Score</span>
        <span className="font-bold text-foreground text-lg">{percentage}%</span>
      </div>
      <div className="h-2 w-full bg-border/30 overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-1000 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
