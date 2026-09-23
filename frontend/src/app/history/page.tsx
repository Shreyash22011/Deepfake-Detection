import Link from "next/link";

interface AnalysisRecord {
  id: string;
  created_at: string;
  media_type: string;
  result?: {
    prediction: string;
    confidence: number;
  };
}

function PredictionBadge({ prediction }: { prediction: string }) {
  const p = prediction.toLowerCase();
  const colorClass =
    p === 'fake' || p === 'synthetic'
      ? 'text-danger'
      : p === 'real'
      ? 'text-success'
      : 'text-warning';
  return (
    <span className={`text-xs font-semibold uppercase ${colorClass}`}>
      {prediction}
    </span>
  );
}

export default async function HistoryPage() {
  let analyses: { id: string; date: string; time: string; type: string; prediction: string; confidence: number }[] = [];
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  try {
    const res = await fetch(`${API_URL}/api/analyses`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      analyses = data.map((item: AnalysisRecord) => {
        const dt = new Date(item.created_at);
        return {
          id: item.id,
          date: dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
          time: dt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          type: item.media_type,
          prediction: item.result?.prediction || '—',
          confidence: item.result?.confidence || 0,
        };
      });
    }
  } catch {
    /* silent */
  }

  return (
    <div className="max-w-7xl mx-auto px-5 sm:px-8 w-full py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-muted mb-1">
            Records
          </p>
          <h1 className="text-2xl font-bold text-foreground">Analysis history</h1>
        </div>
        <Link
          href="/analyze"
          className="px-4 py-2.5 bg-primary text-white text-xs font-semibold rounded-md hover:bg-primary-hover"
        >
          New Analysis
        </Link>
      </div>

      {analyses.length === 0 ? (
        <div className="border border-border rounded-sm bg-surface px-6 py-12 text-center">
          <p className="text-sm font-medium text-foreground mb-1">No analyses yet</p>
          <p className="text-sm text-muted mb-6">Upload a file to run your first analysis.</p>
          <Link href="/analyze" className="text-sm font-medium text-primary hover:underline">
            Start now &rarr;
          </Link>
        </div>
      ) : (
        <div className="border border-border rounded-lg overflow-hidden bg-surface shadow-sm">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-border bg-surface-2/70">
                <th className="px-6 py-3 text-[10px] font-semibold uppercase tracking-widest text-muted">
                  Result
                </th>
                <th className="px-6 py-3 text-[10px] font-semibold uppercase tracking-widest text-muted">
                  Confidence
                </th>
                <th className="px-6 py-3 text-[10px] font-semibold uppercase tracking-widest text-muted">
                  Type
                </th>
                <th className="px-6 py-3 text-[10px] font-semibold uppercase tracking-widest text-muted">
                  Date
                </th>
                <th className="px-6 py-3 text-[10px] font-semibold uppercase tracking-widest text-muted hidden sm:table-cell">
                  ID
                </th>
                <th className="px-6 py-3 text-[10px] font-semibold uppercase tracking-widest text-muted text-right">
                  &nbsp;
                </th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((item, i) => (
                <tr
                  key={item.id}
                  className={`border-b border-border/60 hover:bg-surface-2/60 transition-colors ${
                    i === analyses.length - 1 ? 'border-b-0' : ''
                  }`}
                >
                  <td className="px-6 py-4">
                    <PredictionBadge prediction={item.prediction} />
                  </td>
                  <td className="px-6 py-4 font-mono text-sm font-medium text-foreground">
                    {item.confidence > 0 ? `${(item.confidence * 100).toFixed(1)}%` : '—'}
                  </td>
                  <td className="px-6 py-4 text-sm text-accent capitalize">{item.type}</td>
                  <td className="px-6 py-4 text-sm text-accent">
                    <span>{item.date}</span>
                    <span className="text-muted ml-2 text-xs">{item.time}</span>
                  </td>
                  <td className="px-6 py-4 hidden sm:table-cell">
                    <span className="text-xs font-mono text-muted">{item.id.slice(0, 8)}&hellip;</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      href={`/result/${item.id}`}
                      className="text-xs font-semibold text-primary hover:underline"
                    >
                      View &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
