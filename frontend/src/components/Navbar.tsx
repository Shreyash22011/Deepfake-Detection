import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="bg-panel border-b border-border shadow-sm">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold tracking-tight flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center font-bold text-white">AM</div>
          <span>Authenticity Platform</span>
        </Link>
        <div className="flex gap-6 items-center">
          <Link href="/analyze" className="text-sm font-medium hover:text-primary transition-colors">Analyze</Link>
          <Link href="/history" className="text-sm font-medium hover:text-primary transition-colors">History</Link>
          <Link href="/dashboard" className="text-sm font-medium hover:text-primary transition-colors">Dashboard</Link>
        </div>
      </div>
    </nav>
  );
}
