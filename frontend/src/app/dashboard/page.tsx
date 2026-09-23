import Link from 'next/link';

interface AnalysisRecord { id: string; created_at: string; media_type: string; result?: { prediction?: string; confidence?: number } }

async function getAnalyses(): Promise<AnalysisRecord[]> {
  try { const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/analyses`, { cache: 'no-store' }); return res.ok ? await res.json() : []; } catch { return []; }
}

export default async function DashboardPage() {
  const analyses = await getAnalyses();
  const completedCount = analyses.filter((item) => Boolean(item.result?.prediction)).length;
  const pendingCount = analyses.length - completedCount;
  const fakeCount = analyses.filter((item) => ['fake', 'synthetic'].includes((item.result?.prediction || '').toLowerCase())).length;
  const realCount = analyses.filter((item) => (item.result?.prediction || '').toLowerCase() === 'real').length;
  const mediaTypes = new Set(analyses.map((item) => item.media_type).filter(Boolean)).size;
  const metrics = [['Completed analyses', completedCount.toString()], ['Real detections', realCount.toString()], ['Fake detections', fakeCount.toString()], ['Pending analyses', pendingCount.toString()]];
  const recent = analyses.slice(0, 5);
  return <div className="max-w-7xl mx-auto px-5 sm:px-8 w-full py-10"><div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8"><div><p className="text-xs font-semibold uppercase tracking-widest text-primary mb-2">Workspace overview</p><h1 className="text-2xl font-bold">Analysis dashboard</h1><p className="text-sm text-muted mt-2">A factual view of analyses recorded by the existing service.</p></div><Link href="/analyze" className="self-start sm:self-auto px-4 py-2.5 bg-primary text-white text-sm font-semibold rounded-md hover:bg-primary-hover">New analysis</Link></div><div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">{metrics.map(([label, value]) => <div key={label} className="bg-surface border border-border rounded-lg p-5 shadow-sm"><p className="text-xs uppercase tracking-widest text-muted">{label}</p><p className="text-2xl font-bold mt-3">{value}</p></div>)}</div><section className="bg-surface border border-border rounded-lg shadow-sm overflow-hidden"><div className="flex items-center justify-between px-5 py-4 border-b border-border"><div><h2 className="font-semibold">Recent analyses</h2><p className="text-xs text-muted mt-1">Latest records available from the service</p></div><Link href="/history" className="text-sm font-semibold text-primary hover:underline">View all</Link></div>{recent.length === 0 ? <div className="px-5 py-12 text-center"><p className="text-sm font-medium">No analysis records yet</p><p className="text-sm text-muted mt-1">Run an analysis to begin building your history.</p></div> : <div className="divide-y divide-border">{recent.map((item) => { const prediction = item.result?.prediction || '—'; const tone = prediction.toLowerCase() === 'real' ? 'text-success' : ['fake', 'synthetic'].includes(prediction.toLowerCase()) ? 'text-danger' : 'text-warning'; return <Link key={item.id} href={`/result/${item.id}`} className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-surface-2/60"><div><p className={`text-sm font-semibold uppercase ${tone}`}>{prediction}</p><p className="text-xs text-muted mt-1">{item.media_type || 'Unknown'} · {new Date(item.created_at).toLocaleDateString()}</p></div><span className="font-mono text-sm">{item.result?.confidence ? `${(item.result.confidence * 100).toFixed(1)}%` : '—'}</span></Link>; })}</div>}</section></div>;
}
