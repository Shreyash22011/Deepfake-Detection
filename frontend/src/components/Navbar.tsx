'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_LINKS = [
  { href: '/analyze', label: 'Analyze' },
  { href: '/history', label: 'History' },
  { href: '/dashboard', label: 'Dashboard' },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-surface/95 backdrop-blur border-b border-border">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 h-16 flex items-center justify-between">
        {/* Logo / Brand */}
        <Link
          href="/"
          className="text-[15px] font-semibold text-foreground tracking-tight hover:text-primary transition-colors"
        >
          AI Media Authenticity
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-1" aria-label="Primary navigation">
          {NAV_LINKS.map(({ href, label }) => {
            const isActive =
              href === '/' ? pathname === '/' : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'text-primary bg-primary/8'
                    : 'text-accent hover:text-foreground hover:bg-surface-2'
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
