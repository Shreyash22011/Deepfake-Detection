export default function ConfidenceMeter({ confidence }: { confidence: number }) {
  const percentage = Math.round(confidence * 100);
  let color = 'bg-success';
  if (percentage > 50) color = 'bg-warning';
  if (percentage > 80) color = 'bg-danger';

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-400">Confidence Score</span>
        <span className="font-bold">{percentage}%</span>
      </div>
      <div className="h-4 w-full bg-background rounded-full overflow-hidden border border-border">
        <div 
          className={`h-full ${color} transition-all duration-1000 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
