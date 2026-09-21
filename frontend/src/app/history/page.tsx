import Link from "next/link";

export default function HistoryPage() {
  const mockHistory = [
    { id: 'an-1234', date: '2026-09-20', type: 'video', prediction: 'fake', confidence: 0.89 },
    { id: 'an-1235', date: '2026-09-19', type: 'image', prediction: 'real', confidence: 0.95 },
    { id: 'an-1236', date: '2026-09-18', type: 'audio', prediction: 'uncertain', confidence: 0.55 },
    { id: 'an-1237', date: '2026-09-17', type: 'video', prediction: 'real', confidence: 0.99 },
  ];

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
