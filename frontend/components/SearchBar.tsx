'use client';

interface Props {
  value:    string;
  onChange: (v: string) => void;
  onSearch: (v: string) => void;
  loading:  boolean;
}

export default function SearchBar({ value, onChange, onSearch, loading }: Props) {
  return (
    <div className="flex max-w-2xl mx-auto bg-white border border-border rounded-lg overflow-hidden shadow-sm focus-within:ring-2 focus-within:ring-accent/30 focus-within:border-accent transition-all">
      <div className="flex items-center pl-4 text-ink-light">
        <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
      </div>
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && onSearch(value)}
        placeholder="Enter a property address (e.g. 1234 Elm St, Dallas, TX 75218)"
        className="flex-1 px-3 py-3.5 bg-transparent outline-none text-ink placeholder-ink-light text-sm"
      />
      <button
        onClick={() => onSearch(value)}
        disabled={loading || !value.trim()}
        className="m-1.5 px-6 bg-navy hover:bg-navy-light disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded text-sm transition-colors whitespace-nowrap"
      >
        {loading ? 'Searching…' : 'Search'}
      </button>
    </div>
  );
}
