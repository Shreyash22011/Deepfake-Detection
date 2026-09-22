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

export default async function HistoryPage() {
  let mockHistory: { id: string, date: string, type: string, prediction: string, confidence: number }[] = [];
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  try {
    const res = await fetch(`${API_URL}/api/analyses`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      mockHistory = data.map((item: AnalysisRecord) => ({
        id: item.id,
        date: new Date(item.created_at).toISOString().split('T')[0],
        type: item.media_type,
        prediction: item.result?.prediction || 'pending/error',
        confidence: item.result?.confidence || 0,
      }));
    }
  } catch (e) {
    console.error("Failed to fetch history");
  }

  return (
    <div className="max-w-4xl mx-auto w-full mt-8">
      <h1 className="text-3xl font-bold mb-6">Analysis History</h1>
      
      <div className="bg-panel border border-border rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-background/50 border-b border-border">
            <tr>
              <th className="px-6 py-4 font-semibold text-gray-400">ID</th>
              <th className="px-6 py-4 font-semibold text-gray-400">Date</th>
              <th className="px-6 py-4 font-semibold text-gray-400">Type</th>
              <th className="px-6 py-4 font-semibold text-gray-400">Result</th>
              <th className="px-6 py-4 font-semibold text-gray-400">Confidence</th>
              <th className="px-6 py-4 font-semibold text-gray-400">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {mockHistory.map((item) => (
              <tr key={item.id} className="hover:bg-background/30 transition-colors">
                <td className="px-6 py-4 font-mono">{item.id}</td>
                <td className="px-6 py-4 text-gray-300">{item.date}</td>
                <td className="px-6 py-4 uppercase tracking-wider text-xs">{item.type}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                    item.prediction === 'fake' ? 'bg-danger/20 text-danger' : 
                    item.prediction === 'real' ? 'bg-success/20 text-success' : 
                    'bg-warning/20 text-warning'
                  }`}>
                    {item.prediction}
                  </span>
                </td>
                <td className="px-6 py-4">{(item.confidence * 100).toFixed(0)}%</td>
                <td className="px-6 py-4">
                  <Link href={`/result/${item.id}`} className="text-primary hover:underline text-sm font-medium">
                    View Report
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
