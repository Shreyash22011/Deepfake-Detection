import ConfidenceMeter from './ConfidenceMeter';

interface ResultCardProps {
  prediction: string;
  confidence: number;
  modelName: string;
}

export default function ResultCard({ prediction, confidence, modelName }: ResultCardProps) {
  const isFake = prediction.toLowerCase() === 'fake' || prediction.toLowerCase() === 'synthetic';
  
  return (
    <div className="bg-panel border border-border rounded-xl p-6 shadow-md space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-sm text-gray-400 uppercase tracking-wider font-semibold">Analysis Result</h2>
          <div className="mt-2 flex items-center gap-3">
            <span className={`px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wider ${isFake ? 'bg-danger/20 text-danger border border-danger/30' : 'bg-success/20 text-success border border-success/30'}`}>
              {prediction}
            </span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">Model</p>
          <p className="font-mono text-sm">{modelName}</p>
        </div>
      </div>

      <ConfidenceMeter confidence={confidence} />
      
      <p className="text-sm text-gray-400">
        {isFake 
          ? "High probability of AI manipulation detected. See evidence below." 
          : "No significant signs of AI manipulation detected."}
      </p>
    </div>
  );
}
