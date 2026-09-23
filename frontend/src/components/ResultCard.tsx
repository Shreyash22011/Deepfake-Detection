import ConfidenceMeter from './ConfidenceMeter';

interface ResultCardProps {
  prediction: string;
  confidence: number;
  modelName: string;
}

export default function ResultCard({ prediction, confidence, modelName }: ResultCardProps) {
  const isFake = prediction.toLowerCase() === 'fake' || prediction.toLowerCase() === 'synthetic';

  return (
    <div className="bg-panel border border-border p-8 shadow-sm space-y-8">
      <div className="flex items-start justify-between border-b border-border/50 pb-6">
        <div>
          <h2 className="text-xs text-accent uppercase tracking-widest font-bold">Analysis Result</h2>
          <div className="mt-3 flex items-center gap-3">
            <span className={`text-2xl font-extrabold uppercase tracking-widest ${isFake ? 'text-danger' : 'text-success'}`}>
              {prediction}
            </span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-[10px] text-accent uppercase tracking-widest font-bold">Model</p>
          <p className="font-mono text-sm font-medium mt-1">{modelName}</p>
        </div>
      </div>

      <ConfidenceMeter confidence={confidence} prediction={prediction} />

      <p className="text-sm text-foreground/80 font-light leading-relaxed">
        {isFake
          ? "High probability of AI manipulation detected. See evidence below."
          : "No significant signs of AI manipulation detected."}
      </p>
    </div>
  );
}
