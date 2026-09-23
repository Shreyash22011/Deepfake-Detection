export default function Footer() {
  return (
    <footer className="border-t border-border bg-background mt-auto">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p className="text-sm text-muted">
          AI Media Authenticity Platform &mdash; Academic Research Project
        </p>
        <p className="text-xs text-muted">
          &copy; {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  );
}
